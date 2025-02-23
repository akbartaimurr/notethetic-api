from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import openai

load_dotenv()
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Your local Vite dev server
        "http://localhost:3000",
    ],
    allow_credentials=False,  # Keep this false
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatMessage(BaseModel):
    message: str
    spaceId: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        print(f"Received message: {message.message}") # Add logging
        print(f"Space ID: {message.spaceId}")
        
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        response = await openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": message.message}
            ]
        )
        
        return {"response": response.choices[0].message.content}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}") # Add logging
        raise HTTPException(status_code=500, detail=str(e))

# Add a test endpoint
@app.get("/api/test")
async def test():
    return {"status": "ok"}
