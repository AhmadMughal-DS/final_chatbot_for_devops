from motor.motor_asyncio import AsyncIOMotorClient
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
    chat_entry = {
        "user_id": user_id,
        "message": message,
        "sender": sender,  # "user" or "bot"
        "timestamp": datetime.utcnow()
    }
    await db.chat_history.insert_one(chat_entry)

async def get_chat_history(user_id):
    """Retrieve chat history for a specific user."""
    chats = await db.chat_history.find({"user_id": user_id}).sort("timestamp", 1).to_list(None)
    for chat in chats:
        # Convert ObjectId and datetime for JSON serialization
        chat['_id'] = str(chat['_id'])
        chat['timestamp'] = chat['timestamp'].isoformat() if chat.get('timestamp') else None
    return chats
