from functools import wraps
from flask import jsonify, request
import getpass
from flask import Flask, request
import hashlib
from flask.helpers import make_response
import mysql.connector
import jwt
import datetime as dt

imovies_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="FiE5HF4xHOsPIL9n",
    database="imovies"
)

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
def verify_user_authentication() -> bool:
    """ When a user connects to the CA via the web server interface,
    this function is called to verify this user's credentials. These
    can either be username+passwd or CA signed certificate+certificate
    public key.

    [body]: { "uid": str, "pwd": str }

    Return true if verification is successful, false otherwise."""

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


def generate_certificate(user_JWT):
    """ Generate a new certificate for a given user identified by the given Json Web Token (JWT), sign it with CA's private key."""
    # TODO
    pass


def __store_user_certificate(userID: str):
    """ Send newly issued certificate to the CA database for it to be stored there."""
    # TODO
    pass


if __name__ == "__main__":
    app.run()
