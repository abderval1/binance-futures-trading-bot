from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from .models import UserRole, SubscriptionStatus


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.SUBSCRIBER


class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    subscription_status: SubscriptionStatus
    subscription_expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class APIKeyBase(BaseModel):
    label: str
    testnet: bool = False
    leverage: int = 20
    margin_type: str = "ISOLATED"


class APIKeyCreate(APIKeyBase):
    api_key: str
    secret_key: str

    @validator('leverage')
    def leverage_range(cls, v):
        if v < 1 or v > 125:
            raise ValueError('Leverage must be 1-125')
        return v


class APIKeyResponse(APIKeyBase):
    id: int
    user_id: int
    permissions: dict
    created_at: datetime
    # NEVER return encrypted keys in response
    api_key: Optional[str] = None  # Only for creation confirmation
    secret_key: Optional[str] = None

    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    symbol: str
    side: str
    entry_price: float
    mark_price: float
    quantity: float
    leverage: int
    unrealized_pnl: float
    liquidation_price: float
    margin: float


class PositionResponse(PositionBase):
    id: int
    api_key_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class TradeBase(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float
    realized_pnl: float
    status: str


class TradeResponse(TradeBase):
    id: int
    user_id: int
    api_key_id: int
    fee: float
    order_id: Optional[str]
    executed_at: datetime

    class Config:
        from_attributes = True


class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    order_type: str  # MARKET, LIMIT, STOP, TAKE_PROFIT
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: Optional[str] = "GTC"
    reduce_only: bool = False
    close_position: bool = False


class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    side: str
    status: str
    executed_qty: float
    avg_price: float
    message: Optional[str] = None


# --- Subscription ---
class SubscriptionPlan(BaseModel):
    name: str
    max_accounts: int
    max_daily_trades: int
    features: list[str]
    price_monthly: float


SUBSCRIPTION_PLANS = {
    "basic": SubscriptionPlan(
        name="Basic", max_accounts=2, max_daily_trades=100,
        features=["1 Trading Bot", "Basic Indicators", "Email Support"],
        price_monthly=29.99
    ),
    "pro": SubscriptionPlan(
        name="Pro", max_accounts=5, max_daily_trades=500,
        features=["5 Trading Bots", "Advanced Indicators", "Priority Support", "Webhooks"],
        price_monthly=79.99
    ),
    "enterprise": SubscriptionPlan(
        name="Enterprise", max_accounts=20, max_daily_trades=9999,
        features=["Unlimited Bots", "All Indicators", "VIP Support", "API Access", "Custom Strategies"],
        price_monthly=299.99
    ),
}
