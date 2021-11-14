import datetime
from functools import wraps

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, pkcs12
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID

from flask import Flask, request, jsonify, Response
import hashlib
from flask.helpers import make_response
import mysql.connector
import jwt
import datetime as dt
from subprocess import call

imovies_db = mysql.connector.connect(
    host="172.27.0.3",
    user="certmanager",
    password="SniaVj5YQnKSXXVu",
    database="imovies",
    ssl_ca='../cert/cacert.pem', #root CA
    ssl_verify_cert=True,
    # tls_versions = ["TLSv1.2"]
)
CA_CERTIFICATE = x509.load_pem_x509_certificate(open('../cert/cacert.pem', "rb").read())
INTM_CERTIFICATE = x509.load_pem_x509_certificate(open('../intermediate/intermediate.pem', "rb").read())
INTM_PRIVATE_KEY = serialization.load_pem_private_key(open('../intermediate/private/intermediate.key', "rb").read(), password=None)
INTM_PUB_KEY = INTM_CERTIFICATE.public_key()

cursor = imovies_db.cursor()

app = Flask(__name__)

# TEMPORARY FOR TESTING, should be set up in the environment
app.debug = True
# used to sign jwt
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'


# TODO: refactor this in multiple files, it is a draft auth
def token_required(f):
    """Decorator to check if the request contains a valid JWT.
    Used for routes needing authentication."""

    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])

            query = "SELECT * FROM imovies.users WHERE uid = %s"
            cursor.execute(query, (data['uid'],))

            current_user = cursor.fetchone()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@app.route("/api")
def hello_world():
    return "It works"


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
    pwd = body['pwd']

    # Check user
    hashed_checksum = hashlib.sha1(pwd.encode()).hexdigest()

    query = "SELECT * FROM imovies.users WHERE uid = %s AND pwd = %s"
    cursor.execute(query, (uid, hashed_checksum))

    if cursor.fetchone() != None:  # checks if the user is in the database, if yes generate jwt
        token = jwt.encode(
            {'uid': uid, 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

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
        pvt_key, certificate, additional_certs = pkcs12.load_key_and_certificates(cert, b'')
    #print(certificate.serial_number) just because serial is a useful identifier
        
        INTM_PUB_KEY.verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            # Depends on the algorithm used to create the certificate
            padding.PKCS1v15(),
            certificate.signature_hash_algorithm,)
        token = jwt.encode(
            {'uid': "01", 'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")
        return jsonify({'token': token})
    except:
        if certificate is None:
            print("Bad Format for Received Client Certificate\n")
        else:
            print("Invalid Signature on client certificate\n")
        return make_response("Invalid certificate", 403)


@app.route("/api/info", methods=['GET'])
@token_required
def get_user_info(user: tuple):  # TODO: jwt type?
    """ Retrieve a user's information (i.e. IMovies data) from the CA database."""
    # TODO
    return "Test Auth" + str(user)


def modify_user_info(user_JWT, new_userID: str = "", new_passwd: str = "", new_lastname: str = "",
                     new_firstname: str = "", new_email: str = ""):
    """ Modify given user information on the CA database."""
    # TODO
    pass


@app.route("/api/certificate", methods=['GET'])
# @token_required
def generate_certificate(user=None) -> Response:
    """ Generate a new certificate and corresponding private key for a given user identified by the
    given Json Web Token (JWT), sign it with CA's private key."""
    if user is None:
        user = {'uid': "Jerome"}
    uid = user['uid']
    # source: https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
    user_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    user_certificate = __get_new_certificate(uid, user_private_key)
    user_private_key_str = user_private_key.private_bytes(encoding=Encoding.PEM,
                                                          format=PrivateFormat.PKCS8,
                                                          encryption_algorithm=serialization.NoEncryption()).decode()
    user_certificate_str = user_certificate.public_bytes(Encoding.PEM).decode()

    return jsonify({'private key': user_private_key_str,
                    'certificate': user_certificate_str})


def __get_new_certificate(uid, user_private_key):
    a_day = datetime.timedelta(1, 0, 0)
    certificate_validity_duration = 365  # in number of days
    user_certificate_builder = x509.CertificateBuilder() \
        .subject_name(x509.Name([x509.NameAttribute(NameOID.USER_ID, uid)])) \
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'imovies')])) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(datetime.datetime.today() - a_day) \
        .not_valid_after(datetime.datetime.today() + a_day * certificate_validity_duration) \
        .public_key(user_private_key.public_key())
    return user_certificate_builder.sign(CA_PRIVATE_KEY, hashes.SHA256())


def __store_user_certificate(userID: str):
    """ Send newly issued certificate to the CA database for it to be stored there."""
    # TODO
    pass


if __name__ == "__main__":
    app.run()
