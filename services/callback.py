from fastapi import FastAPI
from services.oura_service import run, get_tokens

app = FastAPI()

run()

@app.get('/callback')
def callback(code: str = None):
    if code:
        get_tokens(code)
        return {"message": "Authorization successful. You can close this tab."}
    else:
        return {"error": "No code found in URL"}