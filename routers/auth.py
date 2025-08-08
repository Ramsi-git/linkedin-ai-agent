from fastapi import APIRouter, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlencode
import os
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

@router.get("/auth/linkedin")
def linkedin_auth():
    scope = "r_liteprofile w_member_social"
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "scope": scope,
        "state": "secure_random_string"
    }
    auth_url = "https://www.linkedin.com/oauth/v2/authorization?" + urlencode(params)
    return RedirectResponse(auth_url)

@router.get("/auth/linkedin/callback")
async def linkedin_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        return {"error": "Missing authorization code"}

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code != 200:
        return {
            "error": "Failed to retrieve access token",
            "details": response.text
        }

    access_token = response.json().get("access_token")
    return {"access_token": access_token}

@router.post("/linkedin/post")
def publish_linkedin_post(access_token: str = Body(...), content: str = Body(...)):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    profile_resp = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    if profile_resp.status_code != 200:
        return {"error": "Failed to fetch profile", "details": profile_resp.text}

    user_urn = profile_resp.json().get("id")
    author = f"urn:li:person:{user_urn}"

    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    post_resp = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_data)
    if post_resp.status_code != 201:
        return {"error": "Failed to publish post", "details": post_resp.text}

    return {"msg": "Post published successfully!"}
