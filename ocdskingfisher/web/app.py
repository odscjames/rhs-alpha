from flask import Flask, request
from ocdskingfisher.config import Config

config = Config()
config.load_user_config()

app = Flask(__name__)

@app.route("/")
def hello():
    return "OCDS Kingfisher"


@app.route("/api/")
def api():
    return "OCDS Kingfisher APIs"


@app.route("/api/v1/")
def api_v1():
    return "OCDS Kingfisher APIs V1"


@app.route("/api/v1/submit/", methods = ['GET', 'POST'])
def api_v1_submit():
    api_key = request.args.get('API_KEY')
    if not api_key or api_key not in config.web_api_keys:
        return "ACCESS DENIED" # TODO proper error

    return "OCDS Kingfisher APIs V1 Submit"

