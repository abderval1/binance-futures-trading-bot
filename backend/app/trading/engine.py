"""
Multi-tenant trading engine for Binance Futures.
Handles position sizing, risk management, and order execution.
"""
from typing import Dict, Optional, List
from datetime import datetime
import asyncio
from ..clients.binance_client import BinanceFuturesClient
from ..database import get_db
from .. import models, schemas
from sqlalchemy.orm import Session
import math


class TradingEngine:
    def __init__(self, api_key_id: int, db: Session):
        self.api_key_id = api_key_id
        self.db = db
        self.client: Optional[BinanceFuturesClient] = None
        self._running = False
        self._tasks: List[asyncio.Task] = []

    async def initialize(self):
        """Load API key and create Binance client"""
        api_key_record = self.db.query(models.APIKey).filter(
            models.APIKey.id == self.api_key_id,
            models.APIKey.is_active == True
        ).first()

        if not api_key_record:
            raise ValueError(f"API key {self.api_key_id} not found or inactive")

        self.api_key_record = api_key_record
        self.client = BinanceFuturesClient(
            api_key_id=self.api_key_id,
            encrypted_api_key=api_key_record.encrypted_api_key,
            encrypted_secret=api_key_record.encrypted_secret_key,
            testnet=api_key_record.testnet
        )
        # Configure leverage and margin
        for position in api_key_record.positions:
            symbol = position.symbol
            await self.client.set_leverage(symbol, api_key_record.leverage)
            await self.client.set_margin_type(symbol, api_key_record.margin_type)

    def _calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        risk_percent: float,
        stop_loss_price: float
    ) -> float:
        """Calculate position size based on risk management"""
        # Get account balance
        balance_data = asyncio.run(self.client.get_balance())
        usdt_balance = next(
            (float(b["balance"]) for b in balance_data if b["asset"] == "USDT"),
            1000.0  # default if not found
        )

        # Risk amount in USDT
        risk_amount = usdt_balance * (risk_percent / 100)

        # Price difference (risk per unit)
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit == 0:
            return 0

        # Position size in base asset
        position_size = risk_amount / risk_per_unit

        # Round to step size
        exchange_info = asyncio.run(self.client.get_exchange_info(symbol))
        filters = exchange_info["symbols"][0]["filters"]
        lot_size_filter = next(f for f in filters if f["filterType"] == "LOT_SIZE")
        step_size = float(lot_size_filter["stepSize"])
        position_size = math.floor(position_size / step_size) * step_size

        return position_size

    def _record_trade(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float,
        fee: float,
        realized_pnl: float,
        order_id: str,
        status: str = "FILLED"
    ):
        """Record trade in database"""
        trade = models.Trade(
            user_id=self.api_key_record.user_id,
            api_key_id=self.api_key_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=int(quantity * 10000),
            price=int(price * 10000),
            fee=int(fee * 10000),
            realized_pnl=int(realized_pnl * 10000),
            order_id=order_id,
            status=status
        )
        self.db.add(trade)
        self.db.commit()

    # ========== PUBLIC API ==========
    async def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reduce_only: bool = False
    ) -> Dict:
        """Place a market order"""
        if not self.client:
            raise RuntimeError("Engine not initialized")

        result = await self.client.place_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity,
            reduce_only=reduce_only
        )

        # Record trade
        self._record_trade(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity,
            price=float(result.get("avgPrice", 0)),
            fee=0,  # TODO: fetch from order
            realized_pnl=0,
            order_id=result["orderId"],
            status=result["status"]
        )

        return result

    async def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict:
        """Place a limit order"""
        result = await self.client.place_order(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )
        return result

    async def place_stop_loss(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> Dict:
        """Place a stop loss order"""
        result = await self.client.place_order(
            symbol=symbol,
            side=side,
            order_type="STOP_MARKET",
            quantity=quantity,
            stop_price=stop_price,
            reduce_only=True
        )
        return result

    async def place_take_profit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> Dict:
        """Place a take profit order"""
        result = await self.client.place_order(
            symbol=symbol,
            side=side,
            order_type="TAKE_PROFIT_MARKET",
            quantity=quantity,
            stop_price=stop_price,
            reduce_only=True
        )
        return result

    async def close_position(self, symbol: str):
        """Close entire position for symbol"""
        positions = await self.client.get_open_positions()
        for pos in positions:
            if pos["symbol"] == symbol:
                qty = float(pos["positionAmt"])
                side = "SELL" if qty > 0 else "BUY"
                return await self.place_market_order(symbol, side, abs(qty), reduce_only=True)
        return {"message": "No open position"}

    async def get_positions(self) -> List[Dict]:
        """Get open positions for this API key"""
        return await self.client.get_open_positions()

    async def set_leverage(self, symbol: str, leverage: int):
        """Set leverage for symbol"""
        return await self.client.set_leverage(symbol, leverage)

    async def sync_positions(self):
        """Sync positions from exchange to DB"""
        positions = await self.client.get_open_positions()
        # Clear existing and recreate
        self.db.query(models.Position).filter(
            models.Position.api_key_id == self.api_key_id
        ).delete()

        for pos in positions:
            db_pos = models.Position(
                api_key_id=self.api_key_id,
                symbol=pos["symbol"],
                side="LONG" if float(pos["positionAmt"]) > 0 else "SHORT",
                entry_price=int(float(pos["entryPrice"]) * 10000),
                mark_price=int(float(pos["markPrice"]) * 10000),
                quantity=int(abs(float(pos["positionAmt"])) * 10000),
                leverage=int(pos["leverage"]),
                unrealized_pnl=int(float(pos["unRealizedProfit"]) * 10000),
                liquidation_price=int(float(pos["liquidationPrice"]) * 10000),
                margin=int(float(pos["positionInitialMargin"]) * 10000)
            )
            self.db.add(db_pos)
        self.db.commit()

    async def start(self):
        """Start the trading engine"""
        await self.initialize()
        self._running = True
        # Start background tasks (position sync, health checks)
        self._tasks.append(asyncio.create_task(self._sync_loop()))

    async def stop(self):
        """Stop the trading engine"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self.client:
            await self.client.close()

    async def _sync_loop(self):
        """Periodic position sync"""
        while self._running:
            try:
                await self.sync_positions()
            except Exception as e:
                print(f"Sync error: {e}")
            await asyncio.sleep(10)
