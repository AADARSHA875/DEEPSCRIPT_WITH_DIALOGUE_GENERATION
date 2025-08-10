# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

# Load API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# Allow your React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/api/generate/")
async def generate_script(req: PromptRequest):
    user_prompt = req.prompt.strip()

    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # Instruction template for better generation
    formatted_prompt = f"""
You are a professional screenplay and dialogue writer.
Follow the user's prompt to produce a creative and natural conversation or scene.

Rules:
- Do NOT repeat the prompt.
- Use character names and realistic exchanges.
- If it's a dialogue, use this format: NAME: line
- If it's a screenplay, follow industry-standard screenplay formatting.
- Keep it engaging and concise.

Example:
Prompt: Write a dialogue between two people deciding what movie to watch.
Output:
JAMES: What about a comedy?
LUCY: I’m not in the mood for something silly.
JAMES: Okay… thriller then?
LUCY: Now you’re talking.

Now respond to the following prompt:
Prompt: {user_prompt}
Output:
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert screenplay and dialogue writer."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.9,
            max_tokens=400
        )

        generated_text = completion.choices[0].message["content"].strip()

        return {"generated_text": generated_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
