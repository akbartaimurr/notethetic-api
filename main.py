from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI  # Correct import for new version

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS - updated origins list
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://notethetic.vercel.app",
        "*"  # Temporarily allow all origins for testing
    ],
    allow_credentials=True,  # Set to True if you need credentials
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly specify methods
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize OpenAI client (correct way in v1.0.0+)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    message: str
    spaceId: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        print(f"Received message: {message.message}")  # Add logging
        print(f"Space ID: {message.spaceId}")
        
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Call OpenAI API using the new interface
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Adjust to correct model if needed
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": message.message}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

# Add a test endpoint
@app.get("/api/test")
async def test():
    return {"status": "ok"}

# Handle OPTIONS request explicitly for CORS preflight
@app.options("/api/chat")
async def options_chat():
    return {"status": "ok"}
