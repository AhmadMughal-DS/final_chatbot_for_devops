from motor.motor_asyncio import AsyncIOMotorClient
from bson.json_util import dumps, loads
from pymongo import MongoClient

from bson import ObjectId
from datetime import datetime

# Set up DB connection for chatbot
client = AsyncIOMotorClient("mongodb+srv://ahmadzafar:IUzvD9FvjOjHoqPR@devops.fzvip.mongodb.net/")
db = client.devops_assignment  

async def create_user(email: str, password: str):
    # Check if user already exists based on email
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        return None  # Account already exists
    user = {"email": email, "password": password}
    result = await db.users.insert_one(user)
    user['_id'] = result.inserted_id
    return user

async def get_user_by_credentials(email: str, password: str):
    return await db.users.find_one({"email": email, "password": password})

async def save_chat(user_id, message, sender):
    """Save a chat message for a specific user."""
    try:
        print(f"Saving chat: user_id={user_id}, sender={sender}, message={message[:20]}...")
        
        # No conversion - store as string for consistency
        chat_entry = {
            "user_id": str(user_id),  # Always store as string
            "message": message,
            "sender": sender,  # "user" or "bot"
            "timestamp": datetime.utcnow()
        }
        result = await db.chat_history.insert_one(chat_entry)
        print(f"Chat saved with ID: {result.inserted_id}")
        return True
    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        return False

async def get_chat_history(user_id):
    """Retrieve chat history for a specific user."""
    try:
        print(f"Getting chat history for user_id: {user_id}")
        
        # Always query by string ID for consistency
        user_id_str = str(user_id)
        print(f"Using string user_id for query: {user_id_str}")
        
        query = {"user_id": user_id_str}
        print(f"Executing query: {query}")
        
        chats = await db.chat_history.find(query).sort("timestamp", 1).to_list(None)
        print(f"Found {len(chats)} chat messages")
        
        for chat in chats:
            # Convert ObjectId and datetime for JSON serialization
            chat['_id'] = str(chat['_id'])
            chat['timestamp'] = chat['timestamp'].isoformat() if chat.get('timestamp') else None
        return chats
    except Exception as e:
        print(f"Error retrieving chat history: {str(e)}")
        return []
