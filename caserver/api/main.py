import datetime
from functools import wraps

from cryptography import x509
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import Encoding, pkcs12, NoEncryption
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID

from flask import Flask, request, jsonify, Response
import hashlib
from flask.helpers import make_response
import mysql.connector
import jwt
import datetime as dt
import base64 as b64

imovies_db = mysql.connector.connect(
    host="172.27.0.3",
    user="certmanager",
    password='SniaVj5YQnKSXXVu',
    database="imovies",
    ssl_ca='../cert/cacert.pem',  # root CA
    ssl_verify_cert=True,
)
cursor = imovies_db.cursor()

CA_CERTIFICATE = x509.load_pem_x509_certificate(
    open('../cert/cacert.pem', "rb").read())
INTM_CERTIFICATE = x509.load_pem_x509_certificate(
    open('../intermediate/intermediate.pem', "rb").read())
INTM_PRIVATE_KEY = serialization.load_pem_private_key(
    open('../intermediate/private/intermediate.key', "rb").read(), password=None)
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
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
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

            current_user = cursor.fetchone()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator

##########################################
#                                        #
#             AUTH ENDPOINTS             #
#                                        #
##########################################
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
        return jsonify({'token': token})
    else:
        return make_response("Wrong credentials", 403)


@app.route("/api/login_with_cert", methods=['POST'])
def verify_user_authentication_cert():
    """ When a user connects to the CA via the web server interface,
    this function is called to verify this user's certificate.
    The certificate must be in PKCS12 format.
    The certificate is checked against the Intermediate CA private key.

    [body]: { "cert": [] } is an array of int

    Return true if verification is successful, false otherwise."""

    # load pkcs12 format
    body = request.get_json()
    cert = bytearray(body["cert"])
    certificate = None
    try:
        pvt_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            cert, b'')
        if certificate == None:
            return make_response("Bad format for certificate", 500)
        # Some useful methods
        # print(certificate.serial_number) just because serial is a useful identifier
        # print(b64.b64encode(certificate.public_bytes(Encoding.PEM)).decode())
        pem_encoding = serialize_cert(certificate)
        #print(deserialize_cert(data), "\n\n", certificate)

        INTM_PUB_KEY.verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            # Depends on the algorithm used to create the certificate
            padding.PKCS1v15(),
            certificate.signature_hash_algorithm,)

        # to do, check that the certificate is actually stored
        query = "SELECT uid FROM imovies.certificates WHERE serial = %s AND pem_encoding = %s AND revoked = 0;"
        cursor.execute(query, (certificate.serial_number, pem_encoding))

        uid = cursor.fetchone()[0]
        if uid != None:  # checks if the user is in the database, if yes generate jwt
            query = "SELECT isadmin FROM imovies.isadmin WHERE uid = %s;"
            cursor.execute(query, (uid,))
            isadmin = cursor.fetchone()[0]
            token = jwt.encode(
                {'uid': uid, 'admin': isadmin, 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")
            return jsonify({'token': token})
        else:
            return make_response("Wrong credentials", 403)
    except:
        if certificate is None:
            print("Bad Format for Received Client Certificate\n")
        else:
            print("Invalid Signature on client certificate\n")
        return make_response("Invalid certificate", 403)

##########################################
#                                        #
#             API ENDPOINTS              #
#                                        #
##########################################


@app.route("/api/info", methods=['GET'])
@token_required
def get_user_info(user):  # TODO: jwt type?
    if user == None:
        return make_response("How are you even here?", 500)
    else:
        print(user)
        return jsonify({"userID": user[0], "password": "****", "firstname": user[2], "lastname": user[1], "email": user[3]})


@app.route("/api/modify", methods=["POST"])
@token_required
def modify_user_info(user):
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
def generate_certificate(user=None) -> Response:
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
        name.encode(), user_private_key, user_certificate, None, NoEncryption())
    pkcs12_bytes = [x for x in bytearray(user_certificate_pkcs12)]
    return jsonify({'pkcs12': pkcs12_bytes})


@app.route("/api/revoke", methods=['POST'])
@token_required
def revoke_cert(user):
    if user == None:
        return make_response("How are you even here?", 500)
    else:
        # load pkcs12 format
        body = request.get_json()
        cert = bytearray(body["cert"])
        certificate = None
        try:
            pvt_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                cert, None)
            if certificate == None:
                return make_response("Bad Format for Cert", 500)
            # Some useful methods
            # print(certificate.serial_number) just because serial is a useful identifier
            # print(b64.b64encode(certificate.public_bytes(Encoding.PEM)).decode())
            pem_encoding = serialize_cert(certificate)
            #print(deserialize_cert(data), "\n\n", certificate)

            INTM_PUB_KEY.verify(
                certificate.signature,
                certificate.tbs_certificate_bytes,
                # Depends on the algorithm used to create the certificate
                padding.PKCS1v15(),
                certificate.signature_hash_algorithm,)
            # to do, check that the certificate is actually stored
            query = "SELECT uid FROM imovies.certificates WHERE serial = %s AND pem_encoding = %s AND revoked = 0;"
            cursor.execute(query, (certificate.serial_number, pem_encoding))

            uid = cursor.fetchone()
            if uid == None:
                return make_response("I don't recognize this certificate dude!", 500)
            else:
                query = "UPDATE imovies.certificates SET revoked = 1 WHERE serial = %s AND uid = %s AND pem_encoding = %s;"
                cursor.execute(
                    query, (certificate.serial_number, user[0], pem_encoding))
                imovies_db.commit()
                ca.revoked += 1
                query = "UPDATE imovies.certificate_issuing_status SET rid = 1, serial=%s, issued=%s, revoked=%s WHERE rid=1;"
                cursor.execute(query, (ca.serial, ca.issued, ca.revoked))
                imovies_db.commit()
                return make_response("Hasta la vista certificate!", 200)
        except cryptography.exceptions.InvalidSignature:
            return make_response("Invalid Certificate", 500)


@app.route("/api/admin", methods=["GET"])
@token_required
def get_ca_status(user):
    if user == None:
        return make_response("WTF?", 500)
    query = "SELECT isadmin FROM imovies.isadmin WHERE uid = %s;"
    cursor.execute(query, (user[0],))
    isadmin = cursor.fetchone()[0]
    if not isadmin:
        return make_response("Not an admin!", 403)
    else:
        return jsonify({"serial": ca.serial, "issued": ca.issued, "revoked": ca.revoked})


def get_new_certificate(uid, user_private_key):
    a_day = datetime.timedelta(1, 0, 0)
    certificate_validity_duration = 365  # in number of days
    user_certificate_builder = x509.CertificateBuilder() \
        .subject_name(x509.Name([x509.NameAttribute(NameOID.USER_ID, uid)])) \
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'caserver.imovies')])) \
        .serial_number(ca.serial) \
        .not_valid_before(datetime.datetime.today() - a_day) \
        .not_valid_after(datetime.datetime.today() + a_day * certificate_validity_duration) \
        .public_key(user_private_key.public_key())
    ca.serial += 1
    ca.issued += 1
    return user_certificate_builder.sign(INTM_PRIVATE_KEY, hashes.SHA256())


if __name__ == "__main__":
    app.run()
