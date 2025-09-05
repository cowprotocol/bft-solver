# api.py
from fastapi import FastAPI, Body, Request
from typing import Dict, List, Optional, Union, Literal, Any, Annotated
from pydantic import BaseModel, Field, StringConstraints
from enum import Enum
import logging

# ------------------------------------------------------------------
# Scalar type aliases (Pydantic v2-friendly; avoid subclassing str)
# ------------------------------------------------------------------
Address = Annotated[str, StringConstraints(pattern=r"^0x[0-9a-fA-F]{40}$")]
Token = Address
TokenAmount = Annotated[str, StringConstraints(pattern=r"^\d+$")]  # decimal digits only
U256 = TokenAmount

# ------------------------------------------------------------------
# TokenInfo
# ------------------------------------------------------------------
class TokenInfo(BaseModel):
    decimals: Optional[int] = None
    symbol: Optional[str] = None
    referencePrice: Optional[str] = None
    availableBalance: TokenAmount
    trusted: bool

# ------------------------------------------------------------------
# Orders
# ------------------------------------------------------------------
class OrderKind(str, Enum):
    sell = "sell"
    buy = "buy"

class OrderClass(str, Enum):
    market = "market"
    limit = "limit"

class SellTokenBalance(str, Enum):
    erc20 = "erc20"
    internal = "internal"
    external = "external"

class BuyTokenBalance(str, Enum):
    erc20 = "erc20"
    internal = "internal"

class SigningScheme(str, Enum):
    eip712 = "eip712"
    ethSign = "ethSign"
    preSign = "preSign"
    eip1271 = "eip1271"

class InteractionData(BaseModel):
    target: Address
    value: TokenAmount
    callData: str

class FlashloanHint(BaseModel):
    lender: Address
    borrower: Address
    token: Token
    amount: TokenAmount

class FeePolicy(BaseModel):
    kind: str
    maxVolumeFactor: Optional[float] = None
    factor: Optional[float] = None

class Order(BaseModel):
    uid: str
    sellToken: Token
    buyToken: Token
    sellAmount: TokenAmount
    fullSellAmount: Optional[TokenAmount] = None
    buyAmount: TokenAmount
    fullBuyAmount: TokenAmount
    feePolicies: Optional[List[FeePolicy]] = None
    validTo: int
    kind: OrderKind
    receiver: Optional[Address] = None
    owner: Address
    partiallyFillable: bool
    preInteractions: List[Any]
    postInteractions: List[InteractionData]
    sellTokenSource: SellTokenBalance = SellTokenBalance.erc20
    buyTokenDestination: BuyTokenBalance = BuyTokenBalance.erc20
    class_: OrderClass = Field(..., alias="class")
    appData: str
    flashloanHint: Optional[FlashloanHint] = None
    signingScheme: SigningScheme
    signature: str

# ------------------------------------------------------------------
# Liquidity
# ------------------------------------------------------------------
class LiquidityKind(str, Enum):
    constantProduct = "constantProduct"
    weightedProduct = "weightedProduct"
    stable = "stable"
    concentratedLiquidity = "concentratedLiquidity"
    limitOrder = "limitOrder"

class TokenReserve(BaseModel):
    balance: TokenAmount
    weight: Optional[str] = None
    scalingFactor: Optional[str] = None

class LiquidityBase(BaseModel):
    id: str
    address: Address
    gasEstimate: str

class ConstantProductPool(LiquidityBase):
    kind: Literal["constantProduct"]
    tokens: Dict[str, TokenReserve]
    fee: str
    router: Address

class WeightedProductPool(LiquidityBase):
    kind: Literal["weightedProduct"]
    tokens: Dict[str, TokenReserve]
    fee: str
    version: Optional[str] = None
    balancer_pool_id: str

class StablePool(LiquidityBase):
    kind: Literal["stable"]
    tokens: Dict[str, TokenReserve]
    amplificationParameter: str
    fee: str
    balancer_pool_id: str

class ConcentratedLiquidityPool(LiquidityBase):
    kind: Literal["concentratedLiquidity"]
    tokens: List[Token]
    sqrtPrice: str
    liquidity: str
    tick: int
    liquidityNet: Dict[str, str]
    fee: str
    router: Address

class ForeignLimitOrder(LiquidityBase):
    kind: Literal["limitOrder"]
    makerToken: Token
    takerToken: Token
    makerAmount: TokenAmount
    takerAmount: TokenAmount
    takerTokenFeeAmount: TokenAmount

Liquidity = Union[
    ConstantProductPool,
    WeightedProductPool,
    StablePool,
    ConcentratedLiquidityPool,
    ForeignLimitOrder,
]

# ------------------------------------------------------------------
# Auction (request) and Solution (response)
# ------------------------------------------------------------------
class Auction(BaseModel):
    id: Optional[str] = None
    tokens: Dict[str, TokenInfo]
    orders: List[Order]
    liquidity: List[Liquidity]
    effectiveGasPrice: TokenAmount
    deadline: str
    surplusCapturingJitOrderOwners: List[Address]

class Trade(BaseModel):
    kind: str
    order: str
    executedAmount: TokenAmount
    fee: Optional[TokenAmount] = None

class Asset(BaseModel):
    token: Token
    amount: TokenAmount

class Interaction(BaseModel):
    kind: str
    internalize: Optional[bool] = None
    id: Optional[str] = None
    inputToken: Optional[Token] = None
    outputToken: Optional[Token] = None
    inputAmount: Optional[TokenAmount] = None
    outputAmount: Optional[TokenAmount] = None
    target: Optional[Address] = None
    value: Optional[TokenAmount] = None
    callData: Optional[str] = None
    allowances: Optional[List[Any]] = None
    inputs: Optional[List[Asset]] = None
    outputs: Optional[List[Asset]] = None

class Call(BaseModel):
    target: Address
    value: TokenAmount
    callData: List[str]

class Flashloan(BaseModel):
    lender: Address
    borrower: Address
    token: Token
    amount: TokenAmount

class Solution(BaseModel):
    id: int
    prices: Dict[str, U256]
    trades: List[Trade]
    preInteractions: Optional[List[Call]] = None
    interactions: List[Interaction]
    postInteractions: Optional[List[Call]] = None
    gas: Optional[int] = None
    flashloans: Optional[Dict[str, Flashloan]] = None

class SolutionResponse(BaseModel):
    solutions: List[Solution]

# ------------------------------------------------------------------
# App + logging + route
# ------------------------------------------------------------------
app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

@app.post("/api/v1/solve", response_model=SolutionResponse)
async def solve(request: Request, auction: Auction = Body(...)) -> SolutionResponse:
    # Log raw and parsed bodies for debugging (comment out in production if noisy)
    raw = await request.body()
    logger.info("Raw body: %s", raw.decode("utf-8", errors="ignore"))
    logger.info("Parsed auction keys: %s", list(auction.model_dump().keys()))

    # Placeholder solution
    solution = Solution(
        id=1,
        prices={},
        trades=[],
        interactions=[]
    )
    return SolutionResponse(solutions=[solution])

# Optional: run directly via `python api.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

