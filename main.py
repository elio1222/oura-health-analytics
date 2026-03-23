from fastapi import FastAPI
import json
from dotenv import load_dotenv
import os
import requests
from pydantic import BaseModel
from datetime import date, timedelta
from services.oura_service import fetch_oura_data

load_dotenv()

app = FastAPI()


"""Daily Sleep Routes"""

@app.get("/sleep/")
async def get_sleep(start_date: str, end_date: str):
    """Get sleep data from specified start and end dates
    Args:
        start_date (str): beginning date
        end_date (str): end date
    """

    url = "https://api.ouraring.com/v2/usercollection/daily_sleep" 
    params={ 
        "start_date": start_date, 
        "end_date": end_date 
    }
    headers = { 
    "Authorization": f"Bearer {os.getenv("ACCESS_TOKEN")}" 
    }
    response = requests.get(url, headers=headers, params=params) 
    
    return "response.json()"

@app.get("/sleep/latest")
def get_latest_sleep():
    """Get latest sleep data(max retries 3)"""

    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    headers = {"Authorization": F"Bearer {os.getenv('ACCESS_TOKEN')}"}
    retries = 3

    for _ in range(retries):
        params = {
            "start_date": today,
            "end_date": today
        }

        response = requests.get(url=url, headers=headers, params=params, timeout=2)
        response.raise_for_status()

        data = response.json()

        if len(data["data"]) > 0:
            return data
        else:
            print(f"no available data for {today}")
            today = today - timedelta(days=1)

@app.get("/sleep/summary")
def get_sleep_summary():
    """Get sleep summary data from the past 7 days, returns avg score"""

    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    headers = {"Authorization": F"Bearer {os.getenv('ACCESS_TOKEN')}"}
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.get(url=url, headers=headers, params=params)
    data = response.json()
    score = 0
    for d in data["data"]:
        score += d["score"]
    avg_score = score / len(data["data"])

    json_data = {
        "avg_score": avg_score,
        "days_tracked": len(data["data"])
    }

    return json_data

"""Sleep Routes"""
@app.get("/sleep/routes")
def get_sleep_routes(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/sleep"
    params = { 
        "start_date": start_date, 
        "end_date": end_date 
    }
    return fetch_oura_data(url=url, params=params)

@app.get("/sleep/routes/latest")
def get_latest_sleep_routes():
    today = date.today() - timedelta(days=4)
    url = "https://api.ouraring.com/v2/usercollection/sleep"
    params = {
        "start_date": today,
        "end_date": today
    }
    data = fetch_oura_data(url=url, params=params)

    while len(data["data"]) == 0:
        today = today - timedelta(days=1)
        new_params = {
            "start_date": today,
            "end_date": today
        }
        print(f"Sleep Routes from {today + timedelta(days=1)} is not available")
        data = fetch_oura_data(url=url, params=new_params)


"""Readiness Routes"""
@app.get("/readiness/")
async def get_readiness(start_date: str, end_date: str):
    """Get readiness data from specified start and end dates
    Args:
        start_date (str): beginning date
        end_date (str): end date
    """

    url = "https://api.ouraring.com/v2/usercollection/daily_readiness" 
    params={ 
        "start_date": start_date, 
        "end_date": end_date 
    }
    headers = { 
    "Authorization": f"Bearer {os.getenv("ACCESS_TOKEN")}" 
    }
    response = requests.get(url, headers=headers, params=params) 
    
    return response.json()

@app.get("/readiness/latest")
def get_readiness_sleep():
    """Get latest readiness data(max retries 3)"""

    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"
    headers = {"Authorization": F"Bearer {os.getenv('ACCESS_TOKEN')}"}
    retries = 3

    for _ in range(retries):
        params = {
            "start_date": today,
            "end_date": today
        }

        response = requests.get(url=url, headers=headers, params=params, timeout=2)
        response.raise_for_status()

        data = response.json()

        if len(data["data"]) > 0:
            return data
        else:
            print(f"no available data for {today}")
            today = today - timedelta(days=1)
