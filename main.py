from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
from apify_client import ApifyClient
import json
from supabase import create_client

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client (simplified)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Apify client
apify_client = ApifyClient("apify_api_RE5Z85Cacc6klMw8aFpYCgdqfmuO2h0qG9TJ")

# Initialize Supabase client
supabase = create_client(
    'https://ybrsfxqrvylxxsahxgkr.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlicnNmeHFydnlseHhzYWh4Z2tyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzNzYwODQsImV4cCI6MjA1NDk1MjA4NH0.rgoH-GIiiYAacsJiM_g_4GRnZfYed1USrApIc8hUnLg'
)

class ChatMessage(BaseModel):
    message: str
    spaceId: str
    lastAIMessage: str | None

class TranscriptRequest(BaseModel):
    url: str

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        messages_for_gpt = [
            {"role": "system", "content": "You are a helpful AI tutor. Consider the following chat history context and question:"}
        ]

        # If there's a last AI message, get a summary and use it
        if message.lastAIMessage:
            # First summarize the last AI message
            summary_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Summarize the following AI response in one short sentence:"},
                    {"role": "user", "content": message.lastAIMessage}
                ]
            )
            summary = summary_completion.choices[0].message.content
            
            # Add context to the conversation
            messages_for_gpt.extend([
                {"role": "system", "content": f"Previous context: {summary}"},
                {"role": "user", "content": message.message}
            ])
        else:
            messages_for_gpt.append({"role": "user", "content": message.message})

        # Get AI response with context
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_for_gpt
        )
        
        ai_response = completion.choices[0].message.content

        # Update history_sum in spaces table
        supabase.table('spaces').update({
            'history_sum': summary if message.lastAIMessage else ai_response
        }).eq('id', message.spaceId).execute()

        return {"response": ai_response}
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcript")
async def generate_transcript(request: TranscriptRequest):
    try:
        # Prepare Actor input
        run_input = {
            "outputFormat": "captions",
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
