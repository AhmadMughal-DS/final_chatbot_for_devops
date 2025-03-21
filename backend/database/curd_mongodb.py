from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Set up DB connection for chatbot
client = MongoClient("mongodb+srv://ahmadzafar:IUzvD9FvjOjHoqPR@devops.fzvip.mongodb.net/")
db = client.devops_assignment  

def create_user(email: str, password: str):
    # Check if user already exists based on email
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return None  # Account already exists
    user = {"email": email, "password": password}
    result = db.users.insert_one(user)
    user['_id'] = result.inserted_id
    return user

def get_user_by_credentials(email: str, password: str):
    return db.users.find_one({"email": email, "password": password})

def save_chat(user_id, message, sender):
    """Save a chat message for a specific user."""
    chat_entry = {
        "user_id": user_id,
        "message": message,
        "sender": sender,  # "user" or "bot"
        "timestamp": datetime.utcnow()
    }
    db.chat_history.insert_one(chat_entry)

def get_chat_history(user_id):
    """Retrieve chat history for a specific user."""
    chats = list(db.chat_history.find({"user_id": user_id}).sort("timestamp", 1))
    for chat in chats:
        # Convert ObjectId and datetime for JSON serialization
        chat['_id'] = str(chat['_id'])
        chat['timestamp'] = chat['timestamp'].isoformat() if chat.get('timestamp') else None
    return chats