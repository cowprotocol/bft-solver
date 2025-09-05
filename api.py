# api.py
from dataclasses import dataclass
from typing import Optional, List
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

@dataclass
class Order:
    uid: str               # hex string
    sellToken: str         # hex string
    buyToken: str          # hex string
    sellAmount: str        # decimal string
    fullSellAmount: Optional[str]
    buyAmount: str
    fullBuyAmount: str
    validTo: int
    kind: str              # "sell" | "buy"
    receiver: Optional[str]
    owner: str
    partiallyFillable: bool
    preInteractions: List
    postInteractions: List
    sellTokenSource: str   # "erc20" | "internal" | "external"
    buyTokenDestination: str  # "erc20" | "internal"
    class_: str            # "market" | "limit"
    appData: str
    signingScheme: str     # "eip712" | "ethSign" | etc.
    signature: str

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        # handle reserved keyword "class"
        if "class" in data:
            data["class_"] = data.pop("class")
        return cls(**data)

    def naive_buffer_solution(self) -> dict:
        solution = {
                "id": 1,
                "prices": {
                    self.sellToken: str(int(self.sellAmount) + 1),
                    self.buyToken: self.buyAmount
                },
                "trades": [
                    {"kind": "fulfillment",
                    "order": self.uid,
                    "fee": "0",
                    "executedAmount": self.sellAmount}
                ],
                "interactions": [],
            }
        return {'solutions': [solution]}

@app.post("/api/v1/solve")
async def solve(request: Request):
    raw = await request.body()
    body = json.loads(raw)
    logger.info(f"Received request {body['id']}")
    order = Order.from_dict(body.get('orders').pop())
    return JSONResponse(content=order.naive_buffer_solution(), status_code=200)

@app.post("/api/v1/notify")
async def notify(request: Request):
    body = await request.json()
    logger.info(f"Received request body: {body}")
    return JSONResponse(content={"message": "OK"}, status_code=200)
