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

    # pagination params
    page      = int(request.args.get("page", 1))
    per_page  = int(request.args.get("per_page", 10))
    search    = request.args.get("search", "")

    db          = current_app.config["MONGO_DB"]
    vector_store= current_app.config["VECTOR_STORE"]

    # pass pagination into service
    data, meta = service.get_animes(db, search, token, vector_store, page, per_page)
    return jsonify({"meta": meta, "animes": data}), 200

@bp.route('/like', methods=['POST'])
def like():
    token = request.headers.get("Authorization")
    if not token:
        return {"error": "Missing token"}, 401
    data = request.json
    db = current_app.config["MONGO_DB"]
    return jsonify(*service.record_like_or_click(db, data["userId"], data["animeId"], data["type"]))

@bp.route('/', methods=['GET'])
def hello():
    return {"message": "Hello from MongoDB"}, 200