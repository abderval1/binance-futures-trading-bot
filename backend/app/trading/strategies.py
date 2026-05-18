"""
Trading Strategies Library
Pre-built strategies for common trading patterns

Includes:
- SMACrossoverStrategy: Simple Moving Average crossover
- AdvancedTrendMomentumStrategy: EMA/RSI/MACD multi-indicator with 2% risk management
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BaseStrategy:
    """Base class for trading strategies"""

    def __init__(self, engine, config: Dict[str, Any]):
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
        if float(position.get("positionAmt", 0)) == 0:
            symbol = position.get("symbol")
            if symbol in self._peak_price:
                del self._peak_price[symbol]
            if symbol in self._trailing_active:
                del self._trailing_active[symbol]


class SMACrossoverStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy
    - Buy when fast SMA crosses above slow SMA
    - Sell when fast SMA crosses below slow SMA
    """

    def __init__(self, engine, config: Dict[str, Any]):
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


class AdvancedTrendMomentumStrategy(BaseStrategy):
    """
    Advanced Trend & Momentum Strategy (Multi-Symbol Scanner)
    
    Entry Criteria (LONG):
      - EMA 50 > EMA 200 (uptrend)
      - MACD histogram crosses from negative to positive (bullish momentum)
      - RSI between 40 and 70 (not overbought)
      
    Entry Criteria (SHORT):
      - EMA 50 < EMA 200 (downtrend)
      - MACD histogram crosses from positive to negative (bearish momentum)
      - RSI between 30 and 60 (not oversold)
    
    Exit Criteria:
      - Take Profit: PnL > 2% of entry
      - Stop Loss: PnL < -1% of entry (hard stop)
      - MACD Reversal: MACD crosses against position direction
      - Trailing: If profit reaches 1.5%, trail stop at 0.5% below peak
    
    Risk Management:
      - 2% of total balance per trade
      - Dynamic position sizing based on stop loss distance
      - Leverage: configurable (default 10x)
      - Max concurrent positions: configurable (default 5)
    """

    def __init__(self, engine, config: Dict[str, Any]):
        super().__init__(engine, config)
        self.risk_pct = config.get("risk_pct", 2.0)
        self.leverage = config.get("leverage", 10)
        self.take_profit_pct_val = config.get("take_profit_pct", 0.02)
        self.stop_loss_pct_val = config.get("stop_loss_pct", 0.01)
        self.trailing_activation_pct = config.get("trailing_activation", 0.015)
        self.trailing_distance_pct = config.get("trailing_distance", 0.005)
        self._peak_price: Dict[str, float] = {}
        self._trailing_active: Dict[str, bool] = {}

    # ==================== INDICATOR CALCULATIONS ====================

    def calculate_ema(self, prices: list, period: int) -> list:
        """Exponential Moving Average"""
        if len(prices) < period:
            return []
        ema = [sum(prices[:period]) / period]
        multiplier = 2 / (period + 1)
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return ema

    def calculate_rsi(self, prices: list, period: int = 14) -> list:
        """Relative Strength Index"""
        if len(prices) <= period:
            return []
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsis = []

        if avg_loss == 0:
            rsis.append(100)
        else:
            rsis.append(100 - (100 / (1 + avg_gain / avg_loss)))

        for i in range(period, len(prices) - 1):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            if avg_loss == 0:
                rsis.append(100)
            else:
                rsis.append(100 - (100 / (1 + avg_gain / avg_loss)))
        return rsis

    def calculate_macd(self, prices: list):
        """MACD (12, 26, 9)"""
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        if not ema_26:
            return [], [], []

        macd_line = []
        diff = len(ema_12) - len(ema_26)
        for i in range(len(ema_26)):
            macd_line.append(ema_12[i + diff] - ema_26[i])

        signal_line = self.calculate_ema(macd_line, 9)
        histogram = []
        if signal_line:
            diff2 = len(macd_line) - len(signal_line)
            for i in range(len(signal_line)):
                histogram.append(macd_line[i + diff2] - signal_line[i])

        return macd_line, signal_line, histogram

    # ==================== ANALYSIS ====================

    async def analyze_symbol(self, symbol: str, current_positions: list) -> Optional[Dict]:
        """
        Analyze a single symbol for entry/exit signals.
        Returns action dict if action taken, None otherwise.
        """
        # 1. Fetch Klines (15m interval, 250 candles for EMA 200)
        try:
            klines = await self.engine.client.get_klines(symbol, "15m", limit=250)
            closes = [float(k[4]) for k in klines]
            highs = [float(k[2]) for k in klines]
            lows = [float(k[3]) for k in klines]
        except Exception as e:
            logger.debug(f"[{symbol}] Failed to fetch klines: {e}")
            return None

        if len(closes) < 200:
            return None

        current_price = closes[-1]

        # 2. Check current open position for this symbol
        pos = next(
            (p for p in current_positions
             if p.get("symbol") == symbol and float(p.get("positionAmt", 0)) != 0),
            None
        )

        # 3. Calculate Indicators
        ema_50_list = self.calculate_ema(closes, 50)
        ema_200_list = self.calculate_ema(closes, 200)
        rsi_list = self.calculate_rsi(closes)
        macd_line, signal_line, hist = self.calculate_macd(closes)

        if not ema_50_list or not ema_200_list or not rsi_list or len(hist) < 2:
            return None

        ema_50 = ema_50_list[-1]
        ema_200 = ema_200_list[-1]
        rsi = rsi_list[-1]
        macd = macd_line[-1]
        signal = signal_line[-1]

        # Determine trend & momentum signals
        uptrend = ema_50 > ema_200
        downtrend = ema_50 < ema_200

        bullish_cross = macd > signal and hist[-1] > 0 and hist[-2] <= 0
        bearish_cross = macd < signal and hist[-1] < 0 and hist[-2] >= 0

        # 4. EXIT LOGIC - Check if we should close existing position
        if pos:
            qty = float(pos["positionAmt"])
            entry = float(pos["entryPrice"])
            is_long = qty > 0

            pnl_pct = ((current_price - entry) / entry) if is_long else ((entry - current_price) / entry)

            should_close = False
            close_reason = ""

            # Track peak price for trailing stop
            if is_long:
                self._peak_price[symbol] = max(self._peak_price.get(symbol, current_price), current_price)
            else:
                self._peak_price[symbol] = min(self._peak_price.get(symbol, current_price), current_price)

            # Check trailing stop activation
            if is_long:
                profit_from_peak = (self._peak_price[symbol] - entry) / entry
            else:
                profit_from_peak = (entry - self._peak_price[symbol]) / entry

            if profit_from_peak >= self.trailing_activation_pct:
                self._trailing_active[symbol] = True

            # Trailing stop logic
            if self._trailing_active.get(symbol, False):
                if is_long:
                    trail_stop_price = self._peak_price[symbol] * (1 - self.trailing_distance_pct)
                    if current_price <= trail_stop_price:
                        should_close = True
                        close_reason = f"TRAILING_STOP (PnL: {pnl_pct*100:.2f}%)"
                else:
                    trail_stop_price = self._peak_price[symbol] * (1 + self.trailing_distance_pct)
                    if current_price >= trail_stop_price:
                        should_close = True
                        close_reason = f"TRAILING_STOP (PnL: {pnl_pct*100:.2f}%)"

            # Take Profit: PnL > 2%
            if pnl_pct >= self.take_profit_pct_val:
                should_close = True
                close_reason = f"TAKE_PROFIT (PnL: {pnl_pct*100:.2f}%)"

            # Stop Loss: PnL < -1%
            elif pnl_pct <= -self.stop_loss_pct_val:
                should_close = True
                close_reason = f"STOP_LOSS (PnL: {pnl_pct*100:.2f}%)"

            # MACD reversal against position
            elif is_long and bearish_cross:
                should_close = True
                close_reason = f"MACD_BEARISH_CROSS (PnL: {pnl_pct*100:.2f}%)"
            elif not is_long and bullish_cross:
                should_close = True
                close_reason = f"MACD_BULLISH_CROSS (PnL: {pnl_pct*100:.2f}%)"

            if should_close:
                logger.info(f"[{symbol}] CLOSING {'LONG' if is_long else 'SHORT'} - Reason: {close_reason}")
                try:
                    await self.engine.close_position(symbol)
                    return {
                        "action": "CLOSE",
                        "symbol": symbol,
                        "reason": close_reason,
                        "pnl_pct": pnl_pct
                    }
                except Exception as e:
                    logger.error(f"[{symbol}] Failed to close position: {e}")
                    return None

            # Position exists but no exit signal - skip
            return None

        # 5. ENTRY LOGIC - Only if no position open for this symbol
        if uptrend and bullish_cross and 40 < rsi < 70:
            logger.info(
                f"[{symbol}] LONG SIGNAL - EMA50={ema_50:.4f} > EMA200={ema_200:.4f}, "
                f"RSI={rsi:.1f}, MACD bullish cross"
            )
            result = await self._execute_trade(symbol, "BUY", current_price, lows[-1])
            if result:
                return {"action": "OPEN_LONG", "symbol": symbol, "price": current_price}

        elif downtrend and bearish_cross and 30 < rsi < 60:
            logger.info(
                f"[{symbol}] SHORT SIGNAL - EMA50={ema_50:.4f} < EMA200={ema_200:.4f}, "
                f"RSI={rsi:.1f}, MACD bearish cross"
            )
            result = await self._execute_trade(symbol, "SELL", current_price, highs[-1])
            if result:
                return {"action": "OPEN_SHORT", "symbol": symbol, "price": current_price}

        return None

    async def _execute_trade(self, symbol: str, side: str, price: float, recent_extreme: float) -> bool:
        """Execute a trade with 2% risk position sizing. Returns True if executed."""
        try:
            # Calculate stop loss distance
            stop_loss_pct = abs(price - recent_extreme) / price
            if stop_loss_pct < 0.005:
                stop_loss_pct = 0.005  # Minimum 0.5% stop distance

            # Set Leverage & Margin Type
            try:
                await self.engine.set_leverage(symbol, self.leverage)
            except Exception as e:
                logger.warning(f"[{symbol}] Leverage set failed (may already be set): {e}")
            
            try:
                await self.engine.set_margin_type(symbol, "ISOLATED")
            except Exception as e:
                logger.warning(f"[{symbol}] Margin type set failed (may already be ISOLATED): {e}")

            # Calculate position size based on 2% risk
            size = await self.engine.calculate_position_size_async(
                symbol, price, self.risk_pct, stop_loss_pct
            )
            if size <= 0:
                logger.warning(f"[{symbol}] Calculated position size is 0, skipping")
                return False

            # Place market order
            logger.info(f"[{symbol}] OPENING {side} - Size: {size}, Price: {price}, Leverage: {self.leverage}x")
            await self.engine.place_market_order(symbol=symbol, side=side, quantity=size)
            return True

        except Exception as e:
            logger.error(f"[{symbol}] Trade execution failed: {e}")
            return False


# Strategy registry
STRATEGIES = {
    "sma_crossover": SMACrossoverStrategy,
    "advanced_trend": AdvancedTrendMomentumStrategy,
}


def create_strategy(name: str, engine, config: Dict[str, Any]):
    strategy_class = STRATEGIES.get(name)
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGIES.keys())}")
    return strategy_class(engine, config)
