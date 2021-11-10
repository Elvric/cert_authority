import getpass

from flask import Flask

app = Flask(__name__)

@app.route("/api")
def hello_world():
    return getpass.getuser()

def verify_user_authentication(userID: str = "", passwd: str = "", user_certificate = None ) -> bool: #TODO: which type for certificate?
    """ When a user connects to the CA via the web server interface,
    this function is called to verify this user's credentials. These
    can either be username+passwd or CA signed certificate+certificate
    public key.
    Return true if verification is successful, false otherwise."""
    if certificate != None:
        #TODO: verify certificate's signature with CA root public key/certificate
        pass
    else:
        #TODO: retrieve stored passwd hash corresponding to userID from CA database ; hash given passwd,
        # compare to stored one
        pass

def get_user_info(user_JWT): #TODO: jwt type?
    """ Retrieve a user's information (i.e. IMovies data) from the CA database."""
    #TODO
    pass

def modify_user_info(user_JWT, new_userID: str = "", new_passwd: str = "", new_lastname: str = "",
                     new_firstname: str = "", new_email: str = ""):
    """ Modify given user information on the CA database."""
    #TODO
    pass

def generate_certificate(user_JWT):
    """ Generate a new certificate for a given user identified by the given Json Web Token (JWT), sign it with CA's private key."""
    #TODO
    pass

def __store_user_certificate(userID: str):
    """ Send newly issued certificate to the CA database for it to be stored there."""
    #TODO
    pass

if __name__ == "__main__":
    app.run()