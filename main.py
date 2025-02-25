from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
from apify_client import ApifyClient
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client with just the API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"  # Explicitly set base URL
)

# Initialize Apify client
apify_client = ApifyClient("apify_api_RE5Z85Cacc6klMw8aFpYCgdqfmuO2h0qG9TJ")

class ChatMessage(BaseModel):
    message: str
    spaceId: str

class TranscriptRequest(BaseModel):
    url: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a stable model
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor for an app called notethetic. You are here to help users with their notes and study materials. You can answer questions, provide explanations, and help users understand complex topics. You can also provide study tips and resources to help users learn more effectively. INCLUDE METADATA IN YOUR RESPONSES"},
                {"role": "user", "content": message.message}
            ]
        )
        
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcript")
async def generate_transcript(request: TranscriptRequest):
    try:
        # Prepare Actor input
        run_input = {
            "outputFormat": "textWithTimestamps",
            "urls": [request.url],
            "maxRetries": 6,
            "proxyOptions": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["BUYPROXIES94952"],
            },
        }

        # Run the Actor and wait for it to finish
        run = apify_client.actor("1s7eXiaukVuOr4Ueg").call(run_input=run_input)

        # Get the transcript from the dataset
        transcript = ""
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            transcript = item.get("transcript", "") or item.get("captions", "")
            break  # We only need the first item

        if not transcript:
            raise HTTPException(status_code=404, detail="No transcript generated")

        return {"transcript": transcript}

    except Exception as e:
        print(f"Error generating transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test():
    return {"status": "ok"}
