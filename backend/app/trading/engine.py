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
import logging

logger = logging.getLogger(__name__)


class TradingEngine:
    def __init__(self, api_key_id: int, db: Session):
        self.api_key_id = api_key_id
        self.db = db
        self.client: Optional[BinanceFuturesClient] = None
        self._running = False
        self._tasks: List[asyncio.Task] = []
        self.api_key_record = None

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

    async def get_usdt_balance(self) -> float:
        """Get USDT balance from Binance account"""
        try:
            # get_balance returns account assets list
            balance_data = await self.client.get_balance()
            for b in balance_data:
                if b.get("asset") == "USDT":
                    # Binance v2 uses 'walletBalance', v1 uses 'balance'
                    bal = b.get("walletBalance") or b.get("balance") or b.get("availableBalance", "0")
                    return float(bal)
            
            # Fallback: try direct account info for totalWalletBalance
            account = await self.client.get_account_info()
            total = account.get("totalWalletBalance", "0")
            return float(total)
        except Exception as e:
            logger.error(f"Failed to get USDT balance: {e}")
            return 0.0

    async def get_all_usdt_pairs(self) -> List[str]:
        """Get all USDT perpetual trading pairs from Binance Futures"""
        try:
            exchange_info = await self.client.get_exchange_info()
            symbols = []
            for s in exchange_info.get("symbols", []):
                # Only USDT-margined perpetual contracts that are currently trading
                if (s.get("quoteAsset") == "USDT"
                        and s.get("contractType") == "PERPETUAL"
                        and s.get("status") == "TRADING"):
                    symbols.append(s["symbol"])
            logger.info(f"Found {len(symbols)} USDT perpetual pairs")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch exchange info: {e}")
            return []

    async def get_top_volume_pairs(self, limit: int = 50) -> List[str]:
        """Get top pairs by 24h volume to focus on liquid markets"""
        try:
            # Fetch all 24h ticker data
            tickers = await self.client._request("GET", "/fapi/v1/ticker/24hr")
            # Filter USDT pairs and sort by quote volume
            usdt_tickers = [
                t for t in tickers
                if t["symbol"].endswith("USDT") and float(t.get("quoteVolume", 0)) > 0
            ]
            usdt_tickers.sort(key=lambda t: float(t["quoteVolume"]), reverse=True)
            top_symbols = [t["symbol"] for t in usdt_tickers[:limit]]
            logger.info(f"Top {limit} pairs by volume: {top_symbols[:10]}...")
            return top_symbols
        except Exception as e:
            logger.error(f"Failed to fetch ticker data: {e}")
            return []

    async def calculate_position_size_async(
        self,
        symbol: str,
        entry_price: float,
        risk_percent: float,
        stop_loss_distance_pct: float
    ) -> float:
        """
        Calculate position size based on 2% risk management (async version).
        
        Args:
            symbol: Trading pair (e.g. BTCUSDT)
            entry_price: Current/entry price
            risk_percent: % of balance to risk (e.g. 2.0 = 2%)
            stop_loss_distance_pct: Stop loss distance as decimal (e.g. 0.01 = 1%)
        
        Returns:
            Position size in base asset units, rounded to lot step size
        """
        # Get account balance
        usdt_balance = await self.get_usdt_balance()
        if usdt_balance <= 0:
            logger.warning("USDT balance is 0, cannot calculate position size")
            return 0

        # Risk amount in USDT (e.g. 2% of $1000 = $20)
        risk_amount = usdt_balance * (risk_percent / 100)

        # Stop loss distance in price terms
        stop_loss_price_distance = entry_price * stop_loss_distance_pct
        if stop_loss_price_distance == 0:
            return 0

        # Position size = Risk / Stop Loss Distance
        # This gives us the notional size that risks exactly risk_amount
        position_size = risk_amount / stop_loss_price_distance

        # Get exchange info for lot size rounding
        try:
            exchange_info = await self.client.get_exchange_info(symbol)
            symbol_info = None
            for s in exchange_info.get("symbols", []):
                if s["symbol"] == symbol:
                    symbol_info = s
                    break

            if symbol_info:
                filters = symbol_info["filters"]
                lot_size_filter = next(
                    (f for f in filters if f["filterType"] == "LOT_SIZE"), None
                )
                if lot_size_filter:
                    step_size = float(lot_size_filter["stepSize"])
                    min_qty = float(lot_size_filter["minQty"])
                    position_size = math.floor(position_size / step_size) * step_size
                    if position_size < min_qty:
                        logger.warning(
                            f"[{symbol}] Position size {position_size} < min qty {min_qty}"
                        )
                        return 0

                # Check MIN_NOTIONAL filter
                min_notional_filter = next(
                    (f for f in filters if f["filterType"] == "MIN_NOTIONAL"), None
                )
                if min_notional_filter:
                    min_notional = float(min_notional_filter.get("notional", 5))
                    notional = position_size * entry_price
                    if notional < min_notional:
                        logger.warning(
                            f"[{symbol}] Notional {notional:.2f} < min {min_notional}"
                        )
                        return 0
        except Exception as e:
            logger.warning(f"[{symbol}] Could not fetch exchange info for sizing: {e}")
            # Fallback: round to 3 decimals
            position_size = math.floor(position_size * 1000) / 1000

        logger.info(
            f"[{symbol}] Position sizing: Balance={usdt_balance:.2f} USDT, "
            f"Risk={risk_amount:.2f} USDT, Size={position_size}"
        )
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
            order_id=str(result.get("orderId", "unknown")),
            status=result.get("status", "FILLED")
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
                if qty == 0:
                    continue
                side = "SELL" if qty > 0 else "BUY"
                return await self.place_market_order(symbol, side, abs(qty), reduce_only=True)
        return {"message": "No open position"}

    async def get_positions(self) -> List[Dict]:
        """Get open positions for this API key"""
        return await self.client.get_open_positions()

    async def set_leverage(self, symbol: str, leverage: int):
        """Set leverage for symbol"""
        return await self.client.set_leverage(symbol, leverage)

    async def set_margin_type(self, symbol: str, margin_type: str):
        """Set margin type (ISOLATED or CROSS) for symbol"""
        return await self.client.set_margin_type(symbol, margin_type)

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
                logger.error(f"Sync error: {e}")
            await asyncio.sleep(10)
