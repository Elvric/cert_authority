from flask import Flask

app = Flask(__name__)

@app.route("/api")
def hello_world():
    return "You reached it"

if __name__ == "__main__":
    app.run(host="0.0.0.0")