from flask import Blueprint, request, jsonify, current_app
from .models import UserModel
from . import service

bp = Blueprint('main', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    db = current_app.config["MONGO_DB"]
    return jsonify(*service.authenticate_user(db, data))

@bp.route('/anime', methods=['GET'])
def get_anime():
    token = request.headers.get("Authorization")
    if not token:
        return {"error": "Missing token"}, 401
    search = request.args.get("search", "")
    db = current_app.config["MONGO_DB"]
    return jsonify(service.get_animes(db, search))

@bp.route('/like', methods=['POST'])
def like():
    token = request.headers.get("Authorization")
    if not token:
        return {"error": "Missing token"}, 401
    data = request.json
    db = current_app.config["MONGO_DB"]
    return jsonify(*service.record_like_or_click(db, data["userId"], data["animeId"]))

@bp.route('/', methods=['GET'])
def hello():
    a=1
    return {"message": "Hello from MongoDB"}, 200