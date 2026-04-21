from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from datetime import date, timedelta, timezone, datetime
from app.services.oura_service import fetch_oura_data, run, get_tokens, param_builder
from app.repositories.db_repo import query_from_db
from app.services.analytics_service import calculate_sleep_summary, calculate_readiness_summary, calculate_stress_summary
from app.services.ai_service import analyze_oura_analytics

load_dotenv()

app = FastAPI()

if not os.getenv("ACCESS_TOKEN") or not os.getenv("REFRESH_TOKEN"):
    run()

@app.get('/callback')
def callback(code: str = None):
    if code:
        get_tokens(code)
        return {"message": "Authorization successful. You can close this tab."}
    else:
        return {"error": "No code found in URL"}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>Oura Analytics</title>
        </head>
        <body>
            <h1>Elio Rocha's Oura Health Analytics REST API</h1>
        </body>
    </html>
    """

"""Daily Sleep"""
@app.get("/sleep/")
async def get_sleep(start_date: str, end_date: str):
    """Get sleep data from specified start and end dates"""
    return query_from_db(type_of_data="sleep", params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/sleep/latest")
def get_latest_sleep():
    """Get latest sleep data(max retries 3)"""
    today = datetime.now(timezone.utc).date()
    return query_from_db(type_of_data="sleep", params=param_builder(start_date=today, end_date=today))

@app.get("/sleep/summary")
def get_sleep_summary():
    """Get sleep summary data from the past 7 days, returns avg score"""
    return calculate_sleep_summary()

"""Daily Readiness"""
@app.get("/readiness/")
async def get_readiness(start_date: str, end_date: str):
    """Get readiness data from specified start and end dates"""
    return query_from_db(type_of_data="readiness", params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/readiness/latest")
def get_latest_readiness():
    """Get latest readiness data(max retries 3)"""
    today = date.today()
    return query_from_db(type_of_data="readiness", params=param_builder(start_date=today, end_date=today))

@app.get("/readiness/summary")
def get_readiness_summary():
    return calculate_readiness_summary()

"""Daily Activity"""
@app.get("/activity/")
def get_activity(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"

    return fetch_oura_data(url=url, params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/activity/latest")
def get_latest_activity():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"

    return fetch_oura_data(url=url, params=param_builder(start_date=today, end_date=today))

"""Daily Stress"""
@app.get("/stress/")
def get_stress(start_date: str, end_date: str):
    return query_from_db(type_of_data="stress", params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/stress/latest")
def get_latest_stress():
    return query_from_db(type_of_data="stress", params=param_builder(start_date=date.today(), end_date=date.today()))


@app.get("/stress/summary")
def get_stress_summary():
    return calculate_stress_summary()

"""Personal Info"""
@app.get("/user/")
def get_personal_info():
    today = date.today()
    url = "https://api.ouraring.com/v2/usercollection/personal_info"

    return fetch_oura_data(url=url, params=param_builder(start_date=today, end_date=today))

"""Heart Rate"""
@app.get("/heart-rate/latest")
def get_bpm():
    now = datetime.now().astimezone()
    earlier = now - timedelta(minutes=60)
    now = now.replace(microsecond=0).isoformat()
    earlier = earlier.replace(microsecond=0).isoformat()
    url = "https://api.ouraring.com/v2/usercollection/heartrate"

    params = {
        "start_datetime": earlier,
        "end_datetime": now
    }
    print(params)
    return fetch_oura_data(url=url, params=params)

"""Sleep Periods (Routes in Oura API Docs)"""
@app.get("/periods/sleep/")
def get_sleep_routes(start_date: str, end_date: str):
    url = "https://api.ouraring.com/v2/usercollection/sleep"

    return fetch_oura_data(url=url, params=param_builder(start_date=start_date, end_date=end_date))

@app.get("/periods/sleep/latest")
def get_latest_sleep_routes():
    today = date.today()
    yesterday = today - timedelta(days=1)
    url = "https://api.ouraring.com/v2/usercollection/sleep"

    return fetch_oura_data(url=url, params=param_builder(start_date=yesterday, end_date=today))

@app.get("/health-assistant/insight")
def get_health_assistant_insight():
    params = param_builder(start_date=date.today() - timedelta(days=6), end_date=date.today())

    sleep_data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_sleep", params=params)

    readiness_data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_readiness", params=params)

    stress_data = fetch_oura_data(url="https://api.ouraring.com/v2/usercollection/daily_stress", params=params)

    sleep_readiness_stress_data = {
        "sleep_data": sleep_data,
        "readiness_data": readiness_data,
        "stress_data": stress_data
    }

    return analyze_oura_analytics(user_data=sleep_readiness_stress_data)

@app.get("/insights/summary")
def get_insights_summary():

    sleep_summary = calculate_sleep_summary()


# insight endpoints
# /insights/summary
# /insights/recommendations
# /insight/ai

