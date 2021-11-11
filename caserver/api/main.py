import getpass

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from flask import Flask, jsonify, Response

import mysql.connector

imovies_db = mysql.connector.connect(
    host="172.27.0.3",
    user="certmanager",
    password="SniaVj5YQnKSXXVu",
    database="imovies"
)

CA_CERTIFICATE = x509.load_pem_x509_certificate(open('/cert/caserver.pem', "rb").read())
CA_PRIVATE_KEY = serialization.load_pem_private_key(open('/cert/caserver.key', "rb").read(), password=None)

app = Flask(__name__)


@app.route("/api")
def hello_world():
    return getpass.getuser()


def verify_user_authentication(userID: str = "", passwd: str = "",
                               user_certificate=None) -> bool:  # TODO: which type for certificate?
    """ When a user connects to the CA via the web server interface,
    this function is called to verify this user's credentials. These
    can either be username+passwd or CA signed certificate+certificate
    public key.
    Return true if verification is successful, false otherwise."""
    if user_certificate != None:
        # TODO: verify certificate's signature with CA root public key/certificate
        pass
    else:
        # TODO: retrieve stored passwd hash corresponding to userID from CA database ; hash given passwd,
        # compare to stored one
        pass


def get_user_info(user_JWT):  # TODO: jwt type?
    """ Retrieve a user's information (i.e. IMovies data) from the CA database."""
    # TODO
    pass


def modify_user_info(user_JWT, new_userID: str = "", new_passwd: str = "", new_lastname: str = "",
                     new_firstname: str = "", new_email: str = ""):
    """ Modify given user information on the CA database."""
    # TODO
    pass

@app.route("/api/certificate", methods=['GET'])
#@token_required
def generate_certificate(user: dict) -> Response:
    """ Generate a new certificate and corresponding private key for a given user identified by the
    given Json Web Token (JWT), sign it with CA's private key."""
    uid = user['uid']
    # source: https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
    user_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    user_certificate_builder = x509.CertificateBuilder() \
        .subject_name(x509.Name([x509.NameAttribute(NameOID.USER_ID, uid)])) \
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'imovies')])) \
        .public_key(user_private_key.public_key())
    certificate = user_certificate_builder.sign(CA_PRIVATE_KEY, hashes.SHA256())
    return jsonify({'private key': user_private_key, 'certificate': certificate})


def __store_user_certificate(userID: str, user_private_key, user_certificate):
    """ Send newly issued certificate to the CA database for it to be stored there."""
    # TODO
    pass


if __name__ == "__main__":
    app.run()
