from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from groq import Groq
import os
from openai import OpenAI



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































































from starlette.concurrency import run_in_threadpool
novita_client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    api_key="sk_koHg-4Cip9AK4shJxPJhjKSM10tCdwLysoAbW85YSaU",  # Replace with your valid key
)

model = "deepseek/deepseek-v3-turbo"
stream = False  # Set to True if you want to handle streaming
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates using the path to frontend directory
template_path = os.path.abspath("frontend")  # or "../frontend" if neede

# to go up a directory
print(f"Resolved template path: {template_path}")

templates = Jinja2Templates(directory=template_path)

class SignupModel(BaseModel):
    email: EmailStr
    password: str

class QueryRequest(BaseModel):
    user_id: str    # new field for user id
    message: str


@app.post("/user")
async def register_user(email: str, password: str):
    user = await run_in_threadpool(create_user, email, password)
    return user


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/signup")
async def signup(email: EmailStr = Form(...), password: str = Form(...),request: Request = None):
    # Try creating a new user. If the user exists, create_user returns None.
    user = await create_user(email, password)
    
    if not user:
        print(f"User already exists: {email}")
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "This email is already registered. Please log in."}
        )
        
    print(f"User created: {user}")
    return RedirectResponse(url="/signin", status_code=303)

@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/signin", response_class=HTMLResponse)
async def get_signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@app.post("/signin")
async def signin_post(email: EmailStr = Form(...), password: str = Form(...)):
    user = await get_user_by_credentials(email, password)
    if user:
        # redirect with user id to show only that user's chat history
        # Convert ObjectId to string for URL
        user_id_str = str(user['_id'])
        return RedirectResponse(url=f"/welcome?user_id={user_id_str}", status_code=303)
    else:
        return RedirectResponse(url="/signin?error=Invalid credentials", status_code=303)

@app.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    user_id = request.query_params.get("user_id", "")
    return templates.TemplateResponse("welcome.html", {"request": request, "user_id": user_id})


@app.post("/ask-devops-doubt")
async def ask_devops_doubt(request: QueryRequest):
    print(f"Received request with user_id: {request.user_id} and message: {request.message[:20]}...")
    
    system_prompt = """
    You are a helpful assistant that solves doubts about the DevOps class taught by Sir Qasim Malik...
    (Include the full original system prompt here)
    """

    try:
        chat_completion = novita_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ],
            stream=stream,
            max_tokens=1000,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Novita AI API: {str(e)}")

    if stream:
        # Optional: Handle streaming responses (basic example)
        full_response = ""
        for chunk in chat_completion:
            part = chunk.choices[0].delta.content or ""
            full_response += part
        response = full_response.strip()
    else:
        try:
            response = chat_completion.choices[0].message.content.strip()
        except (KeyError, IndexError, AttributeError):
            raise HTTPException(status_code=500, detail="Invalid response format from Novita AI.")

    # Save question and answer to DB
    user_save_result = await save_chat(request.user_id, request.message, "user")
    bot_save_result = await save_chat(request.user_id, response, "bot")
    
    print(f"Save results - User message: {user_save_result}, Bot message: {bot_save_result}")

    return {"response": response}

@app.get("/chat-history")
async def get_user_chat_history(user_id: str):
    """Endpoint to retrieve chat history for a specific user"""
    print(f"Chat history endpoint called with user_id: {user_id}")
    
    if not user_id:
        print("Warning: Empty user_id received")
        return {"history": [], "error": "No user ID provided"}
    
    try:
        history = await get_chat_history(user_id)
        print(f"Returning {len(history)} messages for user {user_id}")
        
        # Display first few messages for debugging
        if history:
            for i, msg in enumerate(history[:2]):
                print(f"Message {i+1}: {msg.get('sender')}: {msg.get('message')[:30]}...")
        
        return {"history": history}
    except Exception as e:
        print(f"Error in chat history endpoint: {str(e)}")
        return {"history": [], "error": str(e)}