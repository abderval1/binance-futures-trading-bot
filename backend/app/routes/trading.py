from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from .. import crud, schemas, auth, trading
from ..database import get_db

router = APIRouter(prefix="/trading", tags=["trading"])


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


@router.get("/positions", response_model=list[schemas.PositionResponse])
async def get_positions(
    api_key_id: Optional[int] = None,
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if api_key_id:
        api_key = crud.get_api_key(db, api_key_id=api_key_id)
        if not api_key or api_key.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="API key not found")
        engine = trading.TradingEngine(api_key_id=api_key_id, db=db)
        await engine.initialize()
        try:
            positions = await engine.get_positions()
            return [
                schemas.PositionResponse(
                    id=0,
                    api_key_id=api_key_id,
                    **{k.lower(): v for k, v in pos.items() if k not in ["positionId"]}
                )
                for pos in positions
            ]
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
                        pos["id"] = key.id
                        pos["api_key_id"] = key.id
                        all_positions.append(schemas.PositionResponse.model_validate(pos))
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
