import requests
from dotenv import set_key, load_dotenv
import webbrowser
import os
from urllib.parse import urlencode

load_dotenv()

env_path = ".env"

def run():
    auth_params = {
        "client_id": os.getenv("CLIENT_ID"),
        "redirect_uri": "http://localhost:8000/callback",
        "response_type": "code",
        "scope": "daily heartrate personal stress"
    }

    auth_url = f"https://cloud.ouraring.com/oauth/authorize?{urlencode(auth_params)}"

    print(f"Please visit this URL to authorize: {auth_url}")
    webbrowser.open(auth_url)

def write_tokens(access_token, refresh_token):
    set_key(env_path, "ACCESS_TOKEN", access_token)
    set_key(env_path, "REFRESH_TOKEN", refresh_token)

def get_tokens(code: str):
    auth_code = code
    token_url = "https://api.ouraring.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "redirect_uri": "http://localhost:8000/callback"
    }
    response = requests.post(token_url, data=token_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    write_tokens(access_token, refresh_token)

def refresh_tokens():
    try:
        token_url = "https://api.ouraring.com/oauth/token"
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("REFRESH_TOKEN"),
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
        }
        response = requests.post(token_url, data=token_data)
        new_tokens = response.json()
       
        access_token = new_tokens.get("access_token")
        refresh_token = new_tokens.get("refresh_token")
        write_tokens(access_token, refresh_token)

        global HEADERS
        HEADERS = {"Authorization": f"Bearer {os.getenv("ACCESS_TOKEN")}"}

        return True

    except Exception as e:
        print(e)
        return False