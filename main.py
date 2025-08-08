
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import openai
import requests
from routers import auth
from routers.analytics import router as analytics_router

load_dotenv()

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def read_root():
    return {"msg": "Welcome to the LinkedIn AI Agent!"}

@app.get("/generate-post/")
def generate_post(prompt: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for writing professional LinkedIn posts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        ai_response = response.choices[0].message["content"]
        return {"generated_content": ai_response}
    except Exception as e:
        return {"error": str(e)}

@app.get("/linkedin/profile")
def get_linkedin_profile(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch profile", "details": response.text}
    return response.json()

app.include_router(auth.router)
app.include_router(analytics_router)

