from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from curd_mongodb import create_user, get_user_by_credentials, save_chat, get_chat_history 
from groq import Groq
import os
from openai import OpenAI

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
templates = Jinja2Templates(directory="../frontend")

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