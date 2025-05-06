
# --- app/service.py ---
from .vector_db_service import get_animes_by_clicks
path=r"data\anime-dataset-2023.csv"
import pandas as pd
df=pd.read_csv(path)

def validate_user_data(data):
    required_fields = ["email", "password", "name"]
    for field in required_fields:
        if field not in data:
            return {"error": f"{field} is required"}, 400
    if not isinstance(data["name"], str) or not isinstance(data["email"], str) or not isinstance(data["password"], str):
        return {"error": "Invalid data type"}, 400
    return None

def create_user(db, data):
    validation_error = validate_user_data(data)
    if validation_error:
        return validation_error
    user = db.users.find_one({"email": data["email"]})
    if user:
        return {"error": "User already exists"}, 400
    db.users.insert_one(data)
    return {"message": "User created"}, 201

def login_user(db, data):
    email = ""
    password = ""
    if "email" not in data or not data["email"]:
        return {"error": "Email is required"}, 400
    
    if "password" not in data or not data["password"]:
        return {"error": "Password is required"}, 400
    
    if data["email"]:
        email = data["email"]
    else:
        return {"error": "Email is required"}, 400
    
    if data["password"]:
        password = data["password"]
    else:
        return {"error": "Password is required"}, 400
    
    if not isinstance(email, str) or not isinstance(password, str):
        return {"error": "Invalid data type"}, 400
    
    user = db.users.find_one({"email": email, "password": password})
    if user:
        return user["email"], 200
    return {"error": "Invalid credentials"}, 401

def authenticate_user(db, data):
    if data["type"] == "login":
        return login_user(db, data)
    elif data["type"] == "signup":
        return create_user(db, data)
    

def get_animes(db, search, token, vector_store, page, per_page):
    # get full ordered lists
    result = get_animes_by_clicks(db, search, token)
    tv_list = result.get("TV", [])
    movie_list = result.get("Movies", [])

    # Pagination slicing
    offset = (page - 1) * per_page
    tv_page = tv_list[offset : offset + per_page]
    movie_page = movie_list[offset : offset + per_page]

    # Build response
    data = {"tv": tv_page, "movies": movie_page}
    total_items = len(tv_list) + len(movie_list)
    has_next = offset + per_page < total_items

    meta = {"page": page, "per_page": per_page, "total_items": total_items, "has_next": has_next}
    return data, meta


def record_user_click(db, user_id, anime_id):
    db.clicks.insert_one({"userId": user_id, "animeId": anime_id})
    return {"success": True}, 200

def record_user_like(db, user_id, anime_id):
    db.likes.insert_one({"userId": user_id, "animeId": anime_id})
    return {"success": True}, 200

def record_like_or_click(db, user_id, anime_id, action_type):
    if action_type == "like":
        return record_user_like(db, user_id, anime_id)
    elif action_type == "click":
        return record_user_click(db, user_id, anime_id)
    else:
        return {"error": "Invalid action type"}, 400