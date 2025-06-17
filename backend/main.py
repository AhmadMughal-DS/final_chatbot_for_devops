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

# Set up DB connection for chatbot with error handling
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://ahmadzafar:IUzvD9FvjOjHoqPR@devops.fzvip.mongodb.net/")
DEBUG = os.getenv("DEBUG", "0") == "1"

print(f"Connecting to MongoDB at {MONGODB_URI.split('@')[1] if '@' in MONGODB_URI else 'mongodb'}")
try:
    client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Validate connection
    client.admin.command('ismaster')
    print("MongoDB connection successful")
    db = client.devops_assignment
except Exception as e:
    print(f"MongoDB connection error: {str(e)}")
    # Continue with a dummy DB for development purposes if needed
    if DEBUG:
        print("Running with dummy DB for development")
        from unittest.mock import MagicMock
        client = MagicMock()
        db = MagicMock()
    else:
        # In production, re-raise the exception
        raise

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

# Set up Jinja2 templates using the existing frontend directory
template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
templates = Jinja2Templates(directory=template_path)

print(f"Using template directory: {template_path}")
print(f"Available templates: {os.listdir(template_path)}")
print("for push 3")
# Initialize templates with error handling
try:
    templates = Jinja2Templates(directory=template_path)
    print(f"Successfully initialized templates from {template_path}")
    
    # Verify critical templates exist
    critical_templates = ["welcome.html", "signin.html", "signup.html", "index.html"]
    for template in critical_templates:
        template_file = os.path.join(template_path, template)
        if os.path.exists(template_file):
            print(f"✅ Template exists: {template}")
        else:
            print(f"❌ Missing template: {template}")
            # Create a basic version of the template
            try:
                with open(template_file, 'w') as f:
                    f.write(f'''
                    <!DOCTYPE html>
                    <html>
                    <head><title>DevOps Chatbot - {template}</title></head>
                    <body>
                        <h1>DevOps Chatbot - {template.split('.')[0].title()}</h1>
                        <p>This is an automatically generated template.</p>
                        <p>
                            <a href="/">Home</a> | 
                            <a href="/signin">Sign In</a> | 
                            <a href="/signup">Sign Up</a>
                        </p>
                        <p>{{{{ request }}}} - {{{{ user_id or '' }}}}</p>
                    </body>
                    </html>
                    ''')
                print(f"Created basic template for {template}")
            except Exception as e:
                print(f"Error creating template {template}: {str(e)}")
except Exception as e:
    print(f"Error initializing templates: {str(e)}")
    # Create a minimal templates object that will return static HTML
    from fastapi.templating import _TemplateResponse
    
    class FallbackTemplates:
        def __init__(self):
            self.directory = "fallback"
            
        def TemplateResponse(self, name, context, status_code=200):
            content = f'''
            <!DOCTYPE html>
            <html>
            <head><title>DevOps Chatbot - Fallback</title></head>
            <body>
                <h1>DevOps Chatbot</h1>
                <p>Template {name} could not be loaded.</p>
                <p>
                    <a href="/">Home</a> | 
                    <a href="/signin">Sign In</a> | 
                    <a href="/signup">Sign Up</a>
                </p>
                <p>Context: {context.get("user_id", "") if "user_id" in context else ""}</p>
            </body>
            </html>
            '''
            return HTMLResponse(content=content, status_code=status_code)
    
    templates = FallbackTemplates()



# add webhook
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
    try:
        print("Attempting to render index.html")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        error_msg = f"Error rendering template: {str(e)}"
        print(error_msg)
        # Return a basic HTML response if template rendering fails
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>DevOps Chatbot</title></head>
        <body>
            <h1>DevOps Chatbot</h1>
            <p>The application is running but encountered a template error.</p>
            <p><a href="/signin">Sign In</a> | <a href="/signup">Sign Up</a></p>
            {f"<p>Error details (debug mode): {error_msg}</p>" if DEBUG else ""}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.post("/signup")
async def signup(email: EmailStr = Form(...), password: str = Form(...), request: Request = None):
    try:
        print(f"Processing signup for email: {email}")
        
        # Add fallback for missing Request object (debugging purposes)
        if request is None:
            print("WARNING: Request object is None, creating a mock request")
            from fastapi.testclient import TestClient
            test_client = TestClient(app)
            request = test_client.get("/").request
        
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
    except Exception as e:
        error_msg = f"Error during signup: {str(e)}"
        print(error_msg)
        if DEBUG:
            print(f"Error details: {repr(e)}")
            import traceback
            traceback.print_exc()
        
        # Return a graceful error response
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "An error occurred during signup. Please try again."}
        )

@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    try:
        print("Rendering signup.html template")
        return templates.TemplateResponse("signup.html", {"request": request})
    except Exception as e:
        error_msg = f"Error rendering signup template: {str(e)}"
        print(error_msg)
        if DEBUG:
            import traceback
            traceback.print_exc()
        
        # Return a basic HTML response if template rendering fails
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>DevOps Chatbot - Sign Up</title></head>
        <body>
            <h1>Sign Up</h1>
            <p>Please enter your email and password to create an account.</p>
            <form method="post" action="/signup">
                <div><label>Email: <input type="email" name="email" required></label></div>
                <div><label>Password: <input type="password" name="password" required></label></div>
                <div><button type="submit">Sign Up</button></div>
            </form>
            <p><a href="/">Back to Home</a> | <a href="/signin">Sign In</a></p>
            {f"<p>Error details (debug mode): {error_msg}</p>" if DEBUG else ""}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.get("/signin", response_class=HTMLResponse)
async def get_signin(request: Request):
    try:
        print("Rendering signin.html template")
        # Check if there's an error message in the query parameters
        error = request.query_params.get("error", "")
        return templates.TemplateResponse("signin.html", {"request": request, "error": error})
    except Exception as e:
        error_msg = f"Error rendering signin template: {str(e)}"
        print(error_msg)
        if DEBUG:
            import traceback
            traceback.print_exc()
        
        # Return a basic HTML response if template rendering fails
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>DevOps Chatbot - Sign In</title></head>
        <body>
            <h1>Sign In</h1>
            <p>Please enter your credentials to sign in.</p>
            <form method="post" action="/signin">
                <div><label>Email: <input type="email" name="email" required></label></div>
                <div><label>Password: <input type="password" name="password" required></label></div>
                <div><button type="submit">Sign In</button></div>
            </form>
            <p><a href="/">Back to Home</a> | <a href="/signup">Sign Up</a></p>
            {f"<p>Error details (debug mode): {error_msg}</p>" if DEBUG else ""}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.post("/signin")
async def signin_post(email: EmailStr = Form(...), password: str = Form(...), request: Request = None):
    try:
        print(f"Processing signin for email: {email}")
        
        user = await get_user_by_credentials(email, password)
        if user:
            # Convert ObjectId to string for URL
            try:
                user_id_str = str(user['_id'])
                print(f"User authenticated successfully. ID: {user_id_str}")
                return RedirectResponse(url=f"/welcome?user_id={user_id_str}", status_code=303)
            except Exception as e:
                print(f"Error converting user ID: {str(e)}")
                if DEBUG:
                    print(f"User object: {user}")
                # Fall through to error message
        
        print("Authentication failed: Invalid credentials")
        return RedirectResponse(url="/signin?error=Invalid credentials", status_code=303)
    except Exception as e:
        error_msg = f"Error during signin: {str(e)}"
        print(error_msg)
        if DEBUG:
            print(f"Error details: {repr(e)}")
            import traceback
            traceback.print_exc()
        
        # If request is available, return template response
        if request:
            return templates.TemplateResponse(
                "signin.html", 
                {"request": request, "error": "An error occurred during sign in. Please try again."}
            )
        # Otherwise fall back to redirect
        return RedirectResponse(url="/signin?error=System error", status_code=303)

@app.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    try:
        user_id = request.query_params.get("user_id", "")
        print(f"Welcome route accessed with user_id: {user_id}")
        
        if not user_id:
            print("No user_id provided, redirecting to signin")
            return RedirectResponse(url="/signin", status_code=303)
        
        return templates.TemplateResponse("welcome.html", {"request": request, "user_id": user_id})
    except Exception as e:
        error_msg = f"Error rendering welcome template: {str(e)}"
        print(error_msg)
        if DEBUG:
            import traceback
            traceback.print_exc()
        
        # Return a basic HTML response if template rendering fails
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>DevOps Chatbot - Welcome</title></head>
        <body>
            <h1>Welcome to DevOps Chatbot</h1>
            <p>You have successfully signed in.</p>
            <p><a href="/">Home</a> | <a href="/signin">Sign Out</a></p>
            {f"<p>Error details (debug mode): {error_msg}</p>" if DEBUG else ""}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


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