import datetime
from functools import wraps
from cryptography import x509
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import Encoding, pkcs12, NoEncryption, BestAvailableEncryption
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from subprocess import call
from flask import Flask, request, jsonify, Response
import logging
import hashlib
from flask.helpers import make_response
import mysql.connector
import jwt
import datetime as dt
import base64 as b64
import pysftp

# logging.basicConfig(filename='/var/log/flask_error.log', level=logging.DEBUG)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

imovies_db = mysql.connector.connect(
    host="172.27.0.3",
    user="certmanager",
    password='SniaVj5YQnKSXXVu',
    database="imovies",
    ssl_ca='/etc/nginx/ssl/cacert.pem',  # root CA
    ssl_verify_cert=True,
)
cursor = imovies_db.cursor()

CA_CERTIFICATE = x509.load_pem_x509_certificate(
    open('/etc/nginx/ssl/cacert.pem', "rb").read())
INTM_CERTIFICATE = x509.load_pem_x509_certificate(
    open('/etc/nginx/ssl/cacert.pem', "rb").read())
INTM_PRIVATE_KEY = serialization.load_pem_private_key(
    open('/etc/nginx/ssl/cakey.pem', "rb").read(), password=None)
INTM_PUB_KEY = INTM_CERTIFICATE.public_key()


class CA(object):
    """
        Keeps the state of the CA fetching from db if found or creating the state if first time
        Useful for the admin panel
    """

    def __init__(self):
        try:
            cursor.execute("SELECT * FROM imovies.certificate_issuing_status;")
            data = cursor.fetchone()[1:]
            self.serial = data[0]
            self.issued = data[1]
            self.revoked = data[2]
        except:
            # first time
            self.serial = 1
            self.issued = 0
            self.revoked = 0
            cursor.execute(
                "INSERT INTO imovies.certificate_issuing_status (rid, serial, issued, revoked) VALUES (1,1,0,0);")
            imovies_db.commit()


ca = CA()
app = Flask(__name__)

# TEMPORARY FOR TESTING, should be set up in the environment
app.debug = True
# used to sign jwt
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
# creds for sftp
app.config["SFTP_USER"] = 'sftp_manager'
app.config["SFTP_PWD"] = 'sup3r_s3cr3t_sftp'

#################################################
#                                               #
#                   HELPERS                     #
#                                               #
#################################################


def serialize_cert(cert: x509.Certificate) -> str:
    """
        Input: a Certificate instance, as obtained by pkcs12.load_key_and_certificates
        Output: 
            string representing the b64encoding of the PEM format (as in ----BEGIN CERTIFICATE-----)
            Use this method to push certificates to the db
    """
    return b64.b64encode(cert.public_bytes(Encoding.PEM)).decode()


def deserialize_cert(pem) -> x509.Certificate:
    """
        Input: a string, base64 encoding of a PEM cert from db
        Output: 
                a Certificate instance. Use this method for fetching data from db
    """
    cert = b64.b64decode(pem.encode())
    return x509.load_pem_x509_certificate(cert)

#################################################
#                                               #
#                   APP LOGIC                   #
#                                               #
#################################################


def token_required(f):
    """Decorator to check if the request contains a valid JWT.
    Used for routes needing authentication."""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        is_admin = False
        if 'token' in request.cookies:
            token = request.cookies.get('token')
        if not token:
            return make_response("403 unauthorized", 403)
        try:
            # TO DO: maybe add here the backdoor 1
            # we can decrypt the jwt following the enc algo stored in it, so that
            # hackers can bypass it
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])

            query = "SELECT * FROM imovies.users WHERE uid = %s"
            cursor.execute(query, (data['uid'],))

            is_admin = data.get('isAdmin', False)
            current_user = cursor.fetchone()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, is_admin, *args, **kwargs)

    return decorator

##########################################
#                                        #
#             AUTH ENDPOINTS             #
#                                        #
##########################################


@app.route("/api/is_logged_in", methods=['GET'])
@token_required
def verify_is_user_logged(user, is_admin):
    """ Verify that an user's token cookie is valid
    """
    return make_response(jsonify({"authed": True, "isAdmin": False}), 200)


@app.route("/api/logout", methods=['GET'])
@token_required
def logout_user(user, is_admin):
    res = make_response("OK", 200)
    res.delete_cookie('token')
    return res


@app.route("/api/login", methods=['POST'])
def verify_user_authentication():
    """ When a user connects to the CA via the web server interface,
    this function is called to verify this user's credentials. These
    can either be username+passwd or CA signed certificate+certificate
    public key.

    [body]: { "uid": str, "pwd": str }

    Return 200+token if verification is successful, 403 otherwise."""

    body = request.get_json()
    uid = body['uid']
    pwd = body['password']

    # Check user
    # TO DO: better if we send hash directly
    hashed_checksum = hashlib.sha1(pwd.encode()).hexdigest()

    query = "SELECT * FROM imovies.users WHERE uid = %s AND pwd = %s;"
    cursor.execute(query, (uid, hashed_checksum))

    if cursor.fetchone() != None:  # checks if the user is in the database, if yes generate jwt
        query = "SELECT isadmin FROM imovies.isadmin WHERE uid = %s;"
        cursor.execute(query, (uid,))
        isadmin = cursor.fetchone()[0]
        token = jwt.encode(
            {'uid': uid, 'admin': isadmin, 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

        res = make_response(jsonify({"authed": True, "isAdmin": False}), 200)
        res.set_cookie('token', token, secure=True, httponly=True)
        return res
    else:
        return make_response("Wrong credentials", 403)


@app.route("/api/login_with_cert", methods=['GET'])
def verify_user_authentication_cert():
    """ When a user connects to the CA via the web server interface,
    this function is called to verify this user's certificate.
    The certificate must be stored and not revoked

    Return true if verification is successful, false otherwise."""

    serial = request.headers["X-Custom-Referrer"]
    app.logger.debug(request.headers)
    if serial == None:
        make_response("Header missing", 505)
    # to do, check that the certificate is actually stored
    query = "SELECT uid FROM imovies.certificates WHERE serial = %s AND revoked = 0;"
    cursor.execute(query, (serial))

    uid = cursor.fetchone()[0]
    if uid != None:  # checks if the user is in the database, if yes generate jwt
        query = "SELECT isadmin FROM imovies.isadmin WHERE uid = %s;"
        cursor.execute(query, (uid,))
        isadmin = cursor.fetchone()[0]
        token = jwt.encode(
            {'uid': uid, 'admin': isadmin, 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

        res = make_response(jsonify({"authed": True, "isAdmin": isadmin}), 200)
        res.set_cookie('token', token, secure=True, httponly=True)
        return res

    else:
        return make_response("Wrong credentials", 403)

##########################################
#                                        #
#             API ENDPOINTS              #
#                                        #
##########################################


@app.route("/api/info", methods=['GET'])
@token_required
def get_user_info(user, is_admin):  # TODO: jwt type?
    if user == None:
        return make_response("How are you even here?", 500)
    else:
        print(user)
        return jsonify({"userID": user[0], "password": "****", "firstname": user[2], "lastname": user[1], "email": user[3]})


@app.route("/api/modify", methods=["POST"])
@token_required
def modify_user_info(user, is_admin):
    updated = request.get_json()
    if user == None:
        return make_response("How are you even here?", 500)
    if user[0] != updated["uid"]:
        return make_response("What the fuck!?", 500)
    else:
        if updated["password"] != "****":
            query = "UPDATE imovies.users SET lastname=%s,firstname=%s,email=%s,pwd=%s WHERE uid=%s;"
            hashed_checksum = hashlib.sha1(
                updated["password"].encode()).hexdigest()
            cursor.execute(query, (updated["lastName"], updated["firstName"],
                           updated["email"], hashed_checksum, updated["uid"]))
        else:
            query = "UPDATE imovies.users SET lastname=%s,firstname=%s,email=%s WHERE uid=%s;"
            cursor.execute(
                query, (updated["lastName"], updated["firstName"], updated["email"], updated["uid"]))
        imovies_db.commit()
        return make_response("Updated!", 200)


@app.route("/api/certificate", methods=['GET'])
@token_required
def generate_certificate(user, is_admin) -> Response:
    """ Generate a new certificate and corresponding private key for a given user identified by the
    given Json Web Token (JWT), sign it with INTM_CA's private key."""
    """
    TO DO:
        OK 1 - the certificate must be returned in PKCS12 format (bundle pvt_key + pem cert)
        X 2 - as in OpenSSL, we should keep an internal storage here for certificates plus private keys issued
        X 2b - send pkcs12 also to backup with SFTP?
        OK 3 - define a new table in the database, called certificates. A table entry has the following entries:
            a - serial (PRIMARY KEY): int (serial number of client cert, is unique)
            b - uid (FOREIGN KEY): int (uid of the user to whom this cert belongs)
            c - pem_encoding: str (b64encode of PEM encoding, use serialize_cert for this)
            d - revoked: bool (true: is revoked, false: is active)
    """
    if user is None:
        return make_response("How are you even here?", 500)
    uid = user[0]

    # source: https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
    user_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048)
    user_certificate = get_new_certificate(uid, user_private_key)

    #user_private_key_str = user_private_key.private_bytes(encoding=Encoding.PEM, format=PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption()).decode()
    #user_certificate_str = user_certificate.public_bytes(Encoding.PEM).decode()
    pem_encoding = serialize_cert(user_certificate)

    #store in db
    query = "INSERT INTO imovies.certificates (serial, uid, pem_encoding, revoked) VALUES (%s, %s, %s, %s);"
    val = (user_certificate.serial_number, uid, pem_encoding, int(False))
    cursor.execute(query, val)
    imovies_db.commit()

    # update ca in db
    query = "UPDATE imovies.certificate_issuing_status SET rid = 1, serial=%s, issued=%s, revoked=%s WHERE rid=1;"
    cursor.execute(query, (ca.serial, ca.issued, ca.revoked))
    imovies_db.commit()

    name = str(user_certificate.serial_number)+"_"+uid
    user_certificate_pkcs12 = pkcs12.serialize_key_and_certificates(
        name.encode(), user_private_key, user_certificate, None, BestAvailableEncryption(b"pass"))
    pkcs12_bytes = [x for x in bytearray(user_certificate_pkcs12)]
    return jsonify({'pkcs12': pkcs12_bytes})


@app.route("/api/get_certs", methods=["GET"])
@token_required
def get_all_certs(user):
    """ Returns all certificates issued by the CA. """
    if user is None:
        return make_response("How are you even here?", 500)

    query = "SELECT serial, revoked FROM imovies.certificates WHERE uid=%s ;"
    cursor.execute(query, (user[0], ))
    certs = cursor.fetchall()
    return jsonify(certs)


@app.route("/api/revoke", methods=['POST'])
@token_required
def revoke_cert(user, is_admin):
    if user == None:
        return make_response("How are you even here?", 500)
    else:
        # load pkcs12 format
        body = request.get_json()
        serial = body["serial"]
        uid = user[0]

        certificate = None
        try:
            # to do, check that the certificate is actually stored
            query = "SELECT uid FROM imovies.certificates WHERE serial = %s AND revoked = 0;"
            cursor.execute(query, (serial, ))

            uid = cursor.fetchone()
            if uid == None:
                return make_response("I don't recognize this certificate dude!", 500)
            else:
                query = "UPDATE imovies.certificates SET revoked = 1 WHERE serial = %s AND uid = %s;"
                cursor.execute(
                    query, (serial, user[0], ))
                imovies_db.commit()
                ca.revoked += 1
                query = "UPDATE imovies.certificate_issuing_status SET rid = 1, serial=%s, issued=%s, revoked=%s WHERE rid=1;"
                cursor.execute(query, (ca.serial, ca.issued, ca.revoked))
                imovies_db.commit()
                return make_response("Hasta la vista certificate!", 200)
        except cryptography.exceptions.InvalidSignature:
            return make_response("Invalid Certificate", 500)


@app.route("/api/revoke_all", methods=['POST'])
@token_required
def revoke_all_certs(user, is_admin):
    if user == None:
        return make_response("How are you even here?", 500)
    else:
        try:
            query = "SELECT COUNT(*) FROM imovies.certificates WHERE uid = %s AND revoked = 0;"
            cursor.execute(query, (user[0], ))

            num_certs = cursor.fetchone()

            query = "UPDATE imovies.certificates SET revoked = 1 WHERE uid = %s;"
            cursor.execute(
                query, (user[0],))
            imovies_db.commit()

            ca.revoked += num_certs[0]

            query = "UPDATE imovies.certificate_issuing_status SET rid = 1, serial=%s, issued=%s, revoked=%s WHERE rid=1;"
            cursor.execute(query, (ca.serial, ca.issued, ca.revoked))

            imovies_db.commit()
            return make_response("Hasta la vista certificate!", 200)
        except cryptography.exceptions.InvalidSignature:
            return make_response("Invalid Certificate", 500)


@app.route("/api/admin", methods=["GET"])
@token_required
def get_ca_status(user, is_admin):
    if user == None:
        return make_response("WTF?", 500)

    if not is_admin:
        return make_response("Not an admin!", 403)
    else:
        return jsonify({"serial": ca.serial, "issued": ca.issued, "revoked": ca.revoked})


def get_new_certificate(uid, user_private_key):
    a_day = datetime.timedelta(1, 0, 0)
    certificate_validity_duration = 365  # in number of days
    user_certificate_builder = x509.CertificateBuilder() \
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, u"CH"),\
                                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"VD"),\
                                x509.NameAttribute(NameOID.LOCALITY_NAME, u"Lausanne"),\
                                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"IMovies"),\
                                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"CA"),\
                                x509.NameAttribute(NameOID.COMMON_NAME, f"{uid}")])) \
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, u"CH"),\
                                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"VD"),\
                                x509.NameAttribute(NameOID.LOCALITY_NAME, u"Lausanne"),\
                                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"IMovies"),\
                                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"CA"),\
                                x509.NameAttribute(NameOID.COMMON_NAME, u"imovies")])) \
        .serial_number(ca.serial) \
        .not_valid_before(datetime.datetime.today() - a_day) \
        .not_valid_after(datetime.datetime.today() + a_day * certificate_validity_duration) \
        .public_key(user_private_key.public_key())
    user_certificate_builder.add_extension(x509.ExtendedKeyUsage([x509.ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
    user_certificate_builder.add_extension(x509.KeyUsage(digital_signature=True, content_commitment=True, data_encipherment=True, \
        key_encipherment=True, key_agreement=True, key_cert_sign=False, crl_sign=False, encipher_only=False, decipher_only=False), critical=True)
    user_certificate_builder.add_extension(x509.SubjectKeyIdentifier.from_public_key(user_private_key.public_key()), critical=False)
    ca.serial += 1
    ca.issued += 1
    return user_certificate_builder.sign(INTM_PRIVATE_KEY, hashes.SHA256())
    #cmd_1 = call(f'openssl genrsa \
    #  -out /etc/ca/intermediate/pkcs12_files/{uid}_{ca.serial}.key 2048', shell=True)
    #cmd_2 = call(f'openssl req -config /etc/ca/intermediate/intermediate.cnf \
    #  -key /etc/ca/intermediate/pkcs12_files/{uid}_{ca.serial}.key \
    #  -new -sha256 -subj "/C=CH/ST=VD/L=Lausanne/O=IMovies/CN={uid}_{ca.serial}"\
    #  -out /etc/ca/intermediate/pkcs12_files/{uid}_{ca.serial}.csr',shell=True)
    #cmd_3 = call(f'openssl ca -config /etc/ca/intermediate/intermediate.cnf \
    #  -extensions usr_cert -days 365 -notext -md sha256 \
    #  -in /etc/ca/intermediate/pkcs12_files/{uid}_{ca.serial}.csr \
    #  -out /etc/ca/intermediate/pkcs12_files/{uid}_{ca.serial}.csr', shell=True)


if __name__ == "__main__":
    app.run()
