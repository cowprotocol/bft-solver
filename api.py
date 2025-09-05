from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/v1/solve")
async def solve():
    return JSONResponse(content={"message": "OK"}, status_code=200)

