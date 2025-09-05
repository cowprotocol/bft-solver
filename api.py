from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/v1/solve")
async def solve():
    body = await request.json()
    logger.info(f"Received request body: {body}")
    return JSONResponse(content={"message": "OK"}, status_code=200)

