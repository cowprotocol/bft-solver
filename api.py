# api.py
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

empty_response = {
    "solutions" : []
}

@app.post("/api/v1/solve")
async def solve(request: Request) -> SolutionResponse:
    raw = await request.body()
    body = json.loads(raw)
    logger.info(f"Received request json with keys: {list(body.keys())}")
    return JSONResponse(content=empty_response, status_code=200)

@app.post("/api/v1/notify")
async def notify(request: Request):
    body = await request.json()
    logger.info(f"Received request body: {body}")
    return JSONResponse(content={"message": "OK"}, status_code=200)
