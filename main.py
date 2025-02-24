from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=False,  # Set to False for "*" origins
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    message: str
    spaceId: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        print(f"Received message: {message.message}")
        print(f"Space ID: {message.spaceId}")

        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Changed from gpt-4o-mini
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": message.message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Access response content correctly
        response_content = completion.choices[0].message.content
        return {"response": response_content}

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test():
    return {"status": "ok"}
