"""
Trading Strategies Library
Pre-built strategies for common trading patterns
"""
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from .engine import TradingEngine
from .clients.binance_client import BinanceFuturesClient


class BaseStrategy:
    """Base class for trading strategies"""

    def __init__(self, engine: TradingEngine, config: Dict[str, Any]):
        self.engine = engine
        self.config = config
        self.symbol = config.get("symbol", "BTCUSDT")
        self.position_size = config.get("position_size", 0.001)
        self.stop_loss_pct = config.get("stop_loss_pct", 2.0)
        self.take_profit_pct = config.get("take_profit_pct", 4.0)

    async def on_tick(self, data: Dict[str, Any]):
        """Called on each new candle/tick"""
        raise NotImplementedError

    async def on_position_update(self, position: Dict):
        """Called when position changes"""
        pass


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy
    - Buy when fast SMA crosses above slow SMA
    - Sell when fast SMA crosses below slow SMA
    """

    def __init__(self, engine: TradingEngine, config: Dict[str, Any]):
        super().__init__(engine, config)
        self.fast_period = config.get("fast_period", 10)
        self.slow_period = config.get("slow_period", 30)
        self._last_signal: Optional[str] = None

    async def on_tick(self, data: Dict[str, Any]):
        """data should contain 'klines' from Binance"""
        klines = data.get("klines", [])
        if len(klines) < self.slow_period:
            return

        closes = [float(k[4]) for k in klines[-self.slow_period:]]
        fast_sma = sum(closes[-self.fast_period:]) / self.fast_period
        slow_sma = sum(closes) / self.slow_period

        current_signal = "BUY" if fast_sma > slow_sma else "SELL"

        if current_signal != self._last_signal:
            await self._execute_signal(current_signal, closes[-1])
            self._last_signal = current_signal

    async def _execute_signal(self, signal: str, price: float):
        """Execute trade based on signal"""
        if signal == "BUY":
            # Check if we have a short position to close first
            await self.engine.close_position(self.symbol)
            # Open long
            await self.engine.place_market_order(
                symbol=self.symbol,
                side="BUY",
                quantity=self.position_size
            )
            # Set stop loss / take profit
            stop_loss = price * (1 - self.stop_loss_pct / 100)
            take_profit = price * (1 + self.take_profit_pct / 100)
            await self.engine.place_stop_loss(self.symbol, "SELL", self.position_size, stop_loss)
            await self.engine.place_take_profit(self.symbol, "SELL", self.position_size, take_profit)

        elif signal == "SELL":
            await self.engine.close_position(self.symbol)
            await self.engine.place_market_order(
                symbol=self.symbol,
                side="SELL",
                quantity=self.position_size
            )
            stop_loss = price * (1 + self.stop_loss_pct / 100)
            take_profit = price * (1 - self.take_profit_pct / 100)
            await self.engine.place_stop_loss(self.symbol, "BUY", self.position_size, stop_loss)
            await self.engine.place_take_profit(self.symbol, "BUY", self.position_size, take_profit)


class GridStrategy(BaseStrategy):
    """
    Grid Trading Strategy
    Places buy/sell orders at regular intervals above/below current price
    """

    def __init__(self, engine: TradingEngine, config: Dict[str, Any]):
        super().__init__(engine, config)
        self.grid_levels = config.get("grid_levels", 5)
        self.grid_spacing_pct = config.get("grid_spacing_pct", 1.0)
        self.orders_per_level = config.get("orders_per_level", 1)
        self._orders_placed = False

    async def start(self):
        """Initialize grid orders"""
        if self._orders_placed:
            return

        balance = await self.engine.client.get_balance()
        usdt = next((b for b in balance if b["asset"] == "USDT"), {"balance": 1000})
        total_capital = float(usdt["balance"])

        # Calculate order size per level
        capital_per_level = total_capital / self.grid_levels / 2  # split for buy/sell
        position_size = capital_per_level / 100  # rough estimate

        ticker = await self.engine.client.get_ticker_price(self.symbol)
        current_price = ticker

        # Place buy orders below current price
        for i in range(1, self.grid_levels + 1):
            price = current_price * (1 - i * self.grid_spacing_pct / 100)
            await self.engine.place_limit_order(
                symbol=self.symbol,
                side="BUY",
                quantity=position_size,
                price=price
            )

        # Place sell orders above current price
        for i in range(1, self.grid_levels + 1):
            price = current_price * (1 + i * self.grid_spacing_pct / 100)
            await self.engine.place_limit_order(
                symbol=self.symbol,
                side="SELL",
                quantity=position_size,
                price=price
            )

        self._orders_placed = True


# Strategy registry
STRATEGIES = {
    "sma_crossover": SMACrossoverStrategy,
    "grid": GridStrategy,
}


def create_strategy(name: str, engine: TradingEngine, config: Dict[str, Any]):
    strategy_class = STRATEGIES.get(name)
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGIES.keys())}")
    return strategy_class(engine, config)
