from flask import Flask
from pymongo import MongoClient

client = MongoClient("mongodb+srv://dev:dev@cluster0.hwutjuq.mongodb.net/?retryWrites=true&w=majority")
db = client["capstone"]

def create_app():
    app = Flask(__name__)
    app.config["MONGO_DB"] = db

    from .routes import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/capstone/v1/api')

    return app
