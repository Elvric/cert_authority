import os
from functools import wraps
from cryptography import x509
import cryptography
from cryptography.hazmat.primitives.serialization import Encoding, pkcs12
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

# app setup
app = Flask(__name__)
# should be set up in the environment
app.debug = False
# used to sign jwt
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'

# logging stuff
logging.basicConfig(
    filename='/var/log/flask/server_logs.log', level=logging.DEBUG)

# SFTP config
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None # check ssh backupserver key
# creds 
app.config["SFTP_USER"] = 'cabackup'
app.config["SFTP_PWD"] = 'LZB33eeKa7rhz2PeDjNb'

# mysql connection
imovies_db = mysql.connector.connect(
    host="172.27.0.3",
    user="certmanager",
    password='SniaVj5YQnKSXXVu',
    database="imovies",
    ssl_ca='/etc/nginx/ssl/cacert.pem',  # root CA
    ssl_verify_cert=True,
)
cursor = imovies_db.cursor()

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

        data = None
        try:
            headers = jwt.get_unverified_header(token)

            # BACKDOOR 1: if alg is none, allow tampering
            if headers['alg'] == 'none':
                data = jwt.decode(token, options={'verify_signature': False})
            else:
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
    return make_response(jsonify({"authed": True, "isAdmin": is_admin}), 200)


@app.route("/api/logout", methods=['GET'])
@token_required
def logout_user(user, is_admin):
    res = make_response("OK", 200)
    res.delete_cookie('token')
    app.logger.info("User %s logged out", user[0])
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
        token = jwt.encode(
            {'uid': uid, 'isAdmin': False, 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

        # isAdmin always false here because admin functionalities are only allowed through cert login
        res = make_response(jsonify({"authed": True, "isAdmin": False}), 200)
        res.set_cookie('token', token, secure=True, httponly=True)

        app.logger.info("User %s logged in", uid)

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
    app.logger.debug("SERIAL: "+serial)
    if serial == None:
        make_response("Header missing", 505)
    # to do, check that the certificate is actually stored
    query = "SELECT uid FROM imovies.certificates WHERE serial = %s AND revoked = 0;"
    cursor.execute(query, (serial,))

    uid = cursor.fetchone()[0]
    if uid != None:  # checks if the user is in the database, if yes generate jwt
        query = "SELECT isadmin FROM imovies.isadmin WHERE uid = %s;"
        cursor.execute(query, (uid,))
        isadmin = cursor.fetchone()[0]
        token = jwt.encode(
            {'uid': uid, 'isAdmin': isadmin, 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

        res = make_response(jsonify({"authed": True, "isAdmin": isadmin}), 200)
        res.set_cookie('token', token, secure=True, httponly=True)

        app.logger.info("User %s logged in", uid)

        return res

    else:
        return make_response("Wrong credentials", 403)

##########################################
#                                        #
#            SERVICE ENDPOINTS           #
#                                        #
##########################################


@app.route("/api/info", methods=['GET'])
@token_required
def get_user_info(user, is_admin):  # TODO: jwt type?
    if user == None:
        return make_response("How are you even here?", 500)
    else:
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
    
    if user is None:
        return make_response("How are you even here?", 500)
    uid = user[0]
    query = "SELECT email FROM imovies.users where uid=%s;"
    cursor.execute(query, (uid, ))
    entry = cursor.fetchone()
    email = entry[0]
    query = "SELECT Max(serial) FROM imovies.certificates;"
    cursor.execute(query)
    entry = cursor.fetchone()
    serial = '01'
    if entry[0] is not None:
        serial = entry[0] + 1
        tmp = hex(serial)
        tmp = tmp[2:]
        tmp = tmp.upper()
        if serial < 16:
            serial = '0' + tmp
        else:
            serial = tmp
    cmd = call(["/etc/ca/intermediate/new_cert.sh", uid, serial, email], shell=False)
    if cmd != 0:
        return make_response("err", 503)
    else:
        with open(f"/etc/ca/intermediate/certificates/tmp_cert.p12", 'rb') as f:
            raw = f.read()
            user_key, user_certificate, adds = pkcs12.load_key_and_certificates(
                raw, b'pass')

            #backup cert
            # with pysftp.Connection('172.27.0.4', username=app.config["SFTP_USER"], password=app.config["SFTP_PWD"], cnopts=cnopts) as sftp:
            #     app.logger.debug("SFTP: ESTABLISHED")
            #     try:
            #         res = sftp.put(f"/etc/ca/intermediate/certificates/{serial}_{uid}.p12",f"/backup/{serial}_{uid}.p12", preserve_mtime=True)
            #         app.logger.debug("SFTP: OK")
            #     except:
            #         app.logger.error(traceback.print_exc())
            #         make_response("Error in backing up, no cert issued", 505)
            #
            #store in db
            pem_encoding = serialize_cert(user_certificate)
            query = "INSERT INTO imovies.certificates (serial, uid, pem_encoding, revoked) VALUES (%s, %s, %s, %s);"
            val = (user_certificate.serial_number, uid,
                   pem_encoding, int(False))
            cursor.execute(query, val)
            imovies_db.commit()

            # update ca in db
            app.logger.info(
                "User %s generated a certificate with serial %s", uid, user_certificate.serial_number)
            pkcs12_bytes = [x for x in bytearray(raw)]
            f.close()
            os.remove("/etc/ca/intermediate/certificates/tmp_cert.p12")


        return jsonify({'pkcs12': pkcs12_bytes})


@app.route("/api/get_certs", methods=["GET"])
@token_required
def get_all_certs(user, is_admin):
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
                app.logger.info(
                    "User %s revoked certificate with serial %s", uid[0], serial)

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
            query = "UPDATE imovies.certificates SET revoked = 1 WHERE uid = %s;"
            cursor.execute(
                query, (user[0],))
            imovies_db.commit()

            app.logger.info(
                "User %s revoked all certificates", user[0])

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
        app.logger.info("User %s tried to access admin page", user[0])
        return make_response("Not an admin!", 403)
    else:
        query = "SELECT max(serial) FROM imovies.certificates;"
        cursor.execute(query)
        entry = cursor.fetchone()
        serial = 0
        if entry[0] is not None:
            serial = entry[0]
        query = "SELECT count(*) FROM imovies.certificates"
        cursor.execute(query)
        entry = cursor.fetchone()
        issued = entry[0]
        query = "SELECT count(*) FROM imovies.certificates where revoked = 1"
        cursor.execute(query)
        entry = cursor.fetchone()
        revoked = entry[0]
        query = "SELECT uid, serial, pem_encoding FROM imovies.certificates WHERE revoked=1;"
        cursor.execute(query)
        revoked_certs = cursor.fetchall()

        return jsonify({"serial": int(serial, 16), "issued": issued, "revoked": revoked, "revoked_certs": revoked_certs})


if __name__ == "__main__":
    app.run()
