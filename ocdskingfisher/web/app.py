from flask import Flask, request
from ocdskingfisher.config import Config
from ocdskingfisher.store import Store

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
    # TODO this allows GET API_KEY values only, allow POST and header too!
    api_key = request.args.get('API_KEY')
    if not api_key or api_key not in config.web_api_keys:
        return "ACCESS DENIED" # TODO proper error

    store = Store(config)

    store.load_collection(
        request.form.get('collection_source'),
        request.form.get('collection_data_version'),
        True if request.form.get('collection_sample', '0') in ['1'] else False,
    )



    return "OCDS Kingfisher APIs V1 Submit"

