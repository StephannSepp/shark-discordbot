from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return "<center><h1>Hellow</h1></center>"
