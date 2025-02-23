from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI  # Updated import

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

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    message: str
    spaceId: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        print(f"Received message: {message.message}") # Add logging
        print(f"Space ID: {message.spaceId}")
        
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Changed to 3.5-turbo as it's more cost-effective
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": message.message}
            ]
        )
        
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}") # Add logging
        raise HTTPException(status_code=500, detail=str(e))

# Add a test endpoint
@app.get("/api/test")
async def test():
    return {"status": "ok"}
