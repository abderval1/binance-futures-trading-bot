from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TRADER = "trader"
    SUBSCRIBER = "subscriber"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.SUBSCRIBER)
    is_active = Column(Boolean, default=True)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    subscription_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    api_keys = relationship("APIKey", back_populates="owner", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(100), nullable=False)
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_secret_key = Column(Text, nullable=False)
    testnet = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    leverage = Column(Integer, default=20)
    margin_type = Column(String(20), default="ISOLATED")  # ISOLATED or CROSS
    permissions = Column(JSON, default={})  # {"trade": true, "withdraw": false}
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="api_keys")
    positions = relationship("Position", back_populates="api_key", cascade="all, delete-orphan")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # LONG or SHORT
    entry_price = Column(Integer)  # stored as integer (price * 10000)
    mark_price = Column(Integer)
    quantity = Column(Integer)  # stored as integer (qty * 10000)
    leverage = Column(Integer)
    unrealized_pnl = Column(Integer)  # stored as integer (PNL * 10000)
    liquidation_price = Column(Integer)  # stored as integer (price * 10000)
    margin = Column(Integer)  # stored as integer (margin * 10000)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    api_key = relationship("APIKey", back_populates="positions")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    order_type = Column(String(20), nullable=False)  # MARKET, LIMIT, STOP_LOSS, etc.
    quantity = Column(Integer)  # stored as integer (qty * 10000)
    price = Column(Integer)  # stored as integer (price * 10000)
    fee = Column(Integer)  # stored as integer (fee * 10000)
    realized_pnl = Column(Integer)  # stored as integer (PNL * 10000)
    order_id = Column(String(100))
    status = Column(String(20), default="FILLED")
    executed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trades")


class TradingStrategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    config = Column(JSON, default={})  # strategy-specific parameters
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
