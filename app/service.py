
# --- app/service.py ---

def validate_user_data(data):
    required_fields = ["email", "password", "name"]
    for field in required_fields:
        if field not in data:
            return {"error": f"{field} is required"}, 400
    if not isinstance(data["name"], str) or not isinstance(data["email"], str) or not isinstance(data["password"], str):
        return {"error": "Invalid data type"}, 400
    return None

def create_user(db, data):
    user = db.users.find_one({"email": data["email"]})
    if user:
        return {"error": "User already exists"}, 400
    validate_user_data(data)
    db.users.insert_one(data)
    return {"message": "User created"}, 201

def login_user(db, data):
    email = ""
    password = ""
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
    
def get_animes(db, search):
    if search:
        return list(db.animes.find({"title": {"$regex": search, "$options": "i"}}))
    return list(db.animes.find())

def record_like_or_click(db, user_id, anime_id):
    db.likes.insert_one({"userId": user_id, "animeId": anime_id})
    db.clicks.insert_one({"userId": user_id, "animeId": anime_id})
    return {"success": True}, 200