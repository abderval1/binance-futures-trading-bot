from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from .. import crud, schemas, auth, trading
from ..database import get_db
from ..trading.scanner import start_scanner, stop_scanner, get_scanner_status, get_all_scanners_status

router = APIRouter(prefix="/trading", tags=["trading"])


# ==================== BOT SCANNER ENDPOINTS ====================

class BotStartRequest(BaseModel):
    api_key_id: int
    scan_interval: int = 60         # seconds between scans
    max_positions: int = 5          # max concurrent positions
    risk_pct: float = 2.0           # % of balance to risk per trade
    leverage: int = 10              # default leverage
    top_pairs_limit: int = 0        # 0 = all pairs, N = top N by volume


@router.post("/bot/start")
async def start_bot(
    request: BotStartRequest,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start the autonomous trading bot scanner"""
    # Verify API key belongs to user
    api_key = crud.get_api_key(db, api_key_id=request.api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")

    result = await start_scanner(
        api_key_id=request.api_key_id,
        scan_interval=request.scan_interval,
        max_positions=request.max_positions,
        risk_pct=request.risk_pct,
        leverage=request.leverage,
        top_pairs_limit=request.top_pairs_limit,
    )
    return result


@router.post("/bot/stop/{api_key_id}")
async def stop_bot(
    api_key_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Stop the autonomous trading bot scanner"""
    api_key = crud.get_api_key(db, api_key_id=api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")

    result = await stop_scanner(api_key_id)
    return result


@router.get("/bot/status/{api_key_id}")
async def bot_status(
    api_key_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the status of the bot scanner"""
    api_key = crud.get_api_key(db, api_key_id=api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")

    return get_scanner_status(api_key_id)


@router.get("/bot/status")
async def all_bots_status(
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
):
    """Get status of all running bot scanners"""
    return get_all_scanners_status()


# ==================== TRADING ORDER ENDPOINTS ====================

@router.post("/order", response_model=schemas.OrderResponse)
async def place_order(
    order: schemas.OrderRequest,
    api_key_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify API key belongs to user
    api_key = crud.get_api_key(db, api_key_id=api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")

    engine = trading.TradingEngine(api_key_id=api_key_id, db=db)
    await engine.initialize()

    try:
        if order.order_type == "MARKET":
            result = await engine.place_market_order(
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                reduce_only=order.reduce_only
            )
        elif order.order_type == "LIMIT":
            result = await engine.place_limit_order(
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=order.price
            )
        elif order.order_type in ["STOP", "STOP_MARKET"]:
            result = await engine.place_stop_loss(
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                stop_price=order.stop_price
            )
        elif order.order_type in ["TAKE_PROFIT", "TAKE_PROFIT_MARKET"]:
            result = await engine.place_take_profit(
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                stop_price=order.stop_price
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported order type")

        return schemas.OrderResponse(
            order_id=str(result.get("orderId", "unknown")),
            symbol=order.symbol,
            side=order.side,
            status=result.get("status", "UNKNOWN"),
            executed_qty=float(result.get("executedQty", 0)),
            avg_price=float(result.get("avgPrice", 0)),
            message=None
        )
    finally:
        await engine.stop()


@router.post("/close-position/{symbol}")
async def close_position(
    symbol: str,
    api_key_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    api_key = crud.get_api_key(db, api_key_id=api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")

    engine = trading.TradingEngine(api_key_id=api_key_id, db=db)
    await engine.initialize()
    try:
        result = await engine.close_position(symbol)
        return result
    finally:
        await engine.stop()


from datetime import datetime

@router.get("/positions", response_model=list[schemas.PositionResponse])
async def get_positions(
    api_key_id: Optional[int] = None,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    def map_position(pos: dict, key_id: int) -> schemas.PositionResponse:
        return schemas.PositionResponse(
            id=0,
            api_key_id=key_id,
            symbol=pos.get("symbol", ""),
            side="LONG" if float(pos.get("positionAmt", 0)) > 0 else "SHORT",
            entry_price=float(pos.get("entryPrice", 0)),
            mark_price=float(pos.get("markPrice", 0)),
            quantity=abs(float(pos.get("positionAmt", 0))),
            leverage=int(pos.get("leverage", 1)),
            unrealized_pnl=float(pos.get("unRealizedProfit", 0)),
            liquidation_price=float(pos.get("liquidationPrice", 0)),
            margin=float(pos.get("positionInitialMargin", 0)),
            updated_at=datetime.utcnow()
        )

    if api_key_id:
        api_key = crud.get_api_key(db, api_key_id=api_key_id)
        if not api_key or api_key.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="API key not found")
        engine = trading.TradingEngine(api_key_id=api_key_id, db=db)
        await engine.initialize()
        try:
            positions = await engine.get_positions()
            return [map_position(pos, api_key_id) for pos in positions]
        finally:
            await engine.stop()
    else:
        # Get positions from all user's API keys
        all_positions = []
        for key in current_user.api_keys:
            if key.is_active:
                engine = trading.TradingEngine(api_key_id=key.id, db=db)
                await engine.initialize()
                try:
                    positions = await engine.get_positions()
                    for pos in positions:
                        all_positions.append(map_position(pos, key.id))
                finally:
                    await engine.stop()
        return all_positions


@router.get("/balance/{api_key_id}")
async def get_balance(
    api_key_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    api_key = crud.get_api_key(db, api_key_id=api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")

    engine = trading.TradingEngine(api_key_id=api_key_id, db=db)
    await engine.initialize()
    try:
        balance = await engine.client.get_balance()
        return balance
    finally:
        await engine.stop()
