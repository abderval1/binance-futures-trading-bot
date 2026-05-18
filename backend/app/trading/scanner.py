"""
Autonomous Multi-Pair Trading Scanner

Scans ALL available USDT perpetual pairs on Binance Futures every 60 seconds.
For each pair, evaluates entry and exit criteria using the AdvancedTrendMomentumStrategy.
Automatically opens and closes positions based on signals.

Features:
- Scans all available USDT pairs (or top N by volume) every 60 seconds
- Max concurrent positions (configurable, default 5)
- 2% risk per trade with dynamic position sizing
- Full logging of all decisions
- Trailing stop support (activates at 1.5% profit, trails at 0.5%)
- Graceful start/stop via API
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .engine import TradingEngine
from .strategies import AdvancedTrendMomentumStrategy
from ..database import SessionLocal
from .. import models

logger = logging.getLogger(__name__)


class BotScanner:
    """
    Autonomous trading bot that scans all pairs every 60 seconds.
    
    Usage:
        scanner = BotScanner(api_key_id=1)
        await scanner.start()
        # ... bot runs in background ...
        await scanner.stop()
    """

    def __init__(
        self,
        api_key_id: int,
        scan_interval: int = 60,       # seconds between scans
        max_positions: int = 5,         # max concurrent open positions
        risk_pct: float = 2.0,          # % of balance to risk per trade
        leverage: int = 10,             # default leverage
        top_pairs_limit: int = 0,       # 0 = scan ALL available pairs
    ):
        self.api_key_id = api_key_id
        self.scan_interval = scan_interval
        self.max_positions = max_positions
        self.risk_pct = risk_pct
        self.leverage = leverage
        self.top_pairs_limit = top_pairs_limit

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._engine: Optional[TradingEngine] = None
        self._strategy: Optional[AdvancedTrendMomentumStrategy] = None
        self._db: Optional[Session] = None

        # Stats
        self.started_at: Optional[datetime] = None
        self.last_scan_at: Optional[datetime] = None
        self.total_scans = 0
        self.total_trades_opened = 0
        self.total_trades_closed = 0
        self.last_scan_pairs_count = 0
        self.last_scan_duration = 0.0
        self.errors_count = 0

    @property
    def is_running(self) -> bool:
        return self._running

    def get_status(self) -> Dict:
        """Get current scanner status"""
        return {
            "running": self._running,
            "api_key_id": self.api_key_id,
            "scan_interval_seconds": self.scan_interval,
            "max_positions": self.max_positions,
            "risk_pct": self.risk_pct,
            "leverage": self.leverage,
            "scan_all_pairs": self.top_pairs_limit == 0,
            "pairs_limit": self.top_pairs_limit if self.top_pairs_limit > 0 else "ALL",
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_scan_at": self.last_scan_at.isoformat() if self.last_scan_at else None,
            "total_scans": self.total_scans,
            "total_trades_opened": self.total_trades_opened,
            "total_trades_closed": self.total_trades_closed,
            "last_scan_pairs_count": self.last_scan_pairs_count,
            "last_scan_duration_seconds": round(self.last_scan_duration, 2),
            "errors_count": self.errors_count,
        }

    async def start(self):
        """Start the scanner background loop"""
        if self._running:
            logger.warning("Scanner is already running")
            return

        logger.info("=" * 60)
        logger.info("  BOT SCANNER STARTING")
        logger.info(f"  API Key ID: {self.api_key_id}")
        logger.info(f"  Scan Interval: {self.scan_interval}s")
        logger.info(f"  Max Positions: {self.max_positions}")
        logger.info(f"  Risk Per Trade: {self.risk_pct}%")
        logger.info(f"  Leverage: {self.leverage}x")
        if self.top_pairs_limit == 0:
            logger.info("  Pairs to Scan: ALL available USDT pairs")
        else:
            logger.info(f"  Top Pairs: {self.top_pairs_limit}")
        logger.info("=" * 60)

        # Create DB session
        self._db = SessionLocal()

        # Initialize engine
        self._engine = TradingEngine(api_key_id=self.api_key_id, db=self._db)
        await self._engine.initialize()

        # Initialize strategy
        self._strategy = AdvancedTrendMomentumStrategy(
            engine=self._engine,
            config={
                "risk_pct": self.risk_pct,
                "leverage": self.leverage,
                "take_profit_pct": 0.02,   # 2% TP
                "stop_loss_pct": 0.01,     # 1% SL
            }
        )

        self._running = True
        self.started_at = datetime.utcnow()
        self._task = asyncio.create_task(self._scan_loop())
        logger.info("Bot scanner started successfully!")

    async def stop(self):
        """Stop the scanner"""
        if not self._running:
            logger.warning("Scanner is not running")
            return

        logger.info("Stopping bot scanner...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._engine:
            await self._engine.stop()

        if self._db:
            self._db.close()

        logger.info("Bot scanner stopped.")

    async def _scan_loop(self):
        """Main scanning loop - runs every scan_interval seconds"""
        while self._running:
            try:
                await self._run_single_scan()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.errors_count += 1
                logger.error(f"Scanner error: {e}", exc_info=True)

            # Wait before next scan
            if self._running:
                logger.info(f"Next scan in {self.scan_interval} seconds...")
                await asyncio.sleep(self.scan_interval)

    async def _run_single_scan(self):
        """Execute one full scan of all pairs"""
        scan_start = datetime.utcnow()
        self.total_scans += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"SCAN #{self.total_scans} - {scan_start.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        logger.info(f"{'='*60}")

        # 1. Get current open positions
        try:
            current_positions = await self._engine.client.get_open_positions()
            open_count = len(current_positions)
            logger.info(f"Current open positions: {open_count}/{self.max_positions}")

            for pos in current_positions:
                qty = float(pos.get("positionAmt", 0))
                symbol = pos.get("symbol", "?")
                entry = float(pos.get("entryPrice", 0))
                pnl = float(pos.get("unRealizedProfit", 0))
                side = "LONG" if qty > 0 else "SHORT"
                logger.info(f"  -> {symbol} {side} qty={abs(qty)} entry={entry} PnL={pnl:.4f} USDT")
        except Exception as e:
            logger.error(f"Failed to fetch current positions: {e}")
            current_positions = []
            open_count = 0

        # 2. Get balance
        try:
            balance = await self._engine.get_usdt_balance()
            logger.info(f"USDT Balance: {balance:.2f}")
        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            balance = 0

        if balance < 5:
            logger.warning("Balance too low (< 5 USDT), skipping scan")
            return

        # 3. Get all available USDT pairs or top pairs by volume
        try:
            if self.top_pairs_limit == 0:
                pairs = await self._engine.get_all_usdt_pairs()
            else:
                pairs = await self._engine.get_top_volume_pairs(limit=self.top_pairs_limit)
            self.last_scan_pairs_count = len(pairs)
        except Exception as e:
            logger.error(f"Failed to fetch pairs: {e}")
            return

        if not pairs:
            logger.warning("No pairs found to scan")
            return

        logger.info(f"Scanning {len(pairs)} pairs...")

        # 4. Analyze each pair
        actions_taken = []
        for i, symbol in enumerate(pairs):
            try:
                # Check if we can still open new positions
                can_open_new = open_count < self.max_positions
                
                # Check if this symbol already has a position
                has_position = any(
                    p.get("symbol") == symbol and float(p.get("positionAmt", 0)) != 0
                    for p in current_positions
                )

                # Skip if no position and we're at max capacity
                if not has_position and not can_open_new:
                    continue

                # Analyze the symbol
                result = await self._strategy.analyze_symbol(symbol, current_positions)

                if result:
                    actions_taken.append(result)
                    action = result.get("action", "")

                    if "OPEN" in action:
                        self.total_trades_opened += 1
                        open_count += 1
                    elif action == "CLOSE":
                        self.total_trades_closed += 1
                        open_count -= 1
                        # Remove from current_positions to allow re-entry
                        current_positions = [
                            p for p in current_positions
                            if p.get("symbol") != symbol
                        ]

                # Small delay between pairs to avoid rate limits
                await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"[{symbol}] Analysis error: {e}")
                self.errors_count += 1

        # 5. Scan summary
        scan_end = datetime.utcnow()
        self.last_scan_at = scan_end
        self.last_scan_duration = (scan_end - scan_start).total_seconds()

        logger.info(f"\n--- SCAN #{self.total_scans} COMPLETE ---")
        logger.info(f"Duration: {self.last_scan_duration:.1f}s")
        logger.info(f"Pairs scanned: {len(pairs)}")
        logger.info(f"Actions taken: {len(actions_taken)}")
        for action in actions_taken:
            logger.info(f"  -> {action}")
        logger.info(f"Open positions: {open_count}/{self.max_positions}")
        logger.info(f"Lifetime: Opened={self.total_trades_opened}, Closed={self.total_trades_closed}")
        logger.info(f"{'='*60}\n")


# ==================== GLOBAL SCANNER MANAGER ====================

# Global dict to hold active scanners per api_key_id
_active_scanners: Dict[int, BotScanner] = {}


async def start_scanner(
    api_key_id: int,
    scan_interval: int = 60,
    max_positions: int = 5,
    risk_pct: float = 2.0,
    leverage: int = 10,
    top_pairs_limit: int = 0,
) -> Dict:
    """Start a scanner for an API key"""
    if api_key_id in _active_scanners and _active_scanners[api_key_id].is_running:
        return {"status": "already_running", **_active_scanners[api_key_id].get_status()}

    scanner = BotScanner(
        api_key_id=api_key_id,
        scan_interval=scan_interval,
        max_positions=max_positions,
        risk_pct=risk_pct,
        leverage=leverage,
        top_pairs_limit=top_pairs_limit,
    )
    await scanner.start()
    _active_scanners[api_key_id] = scanner
    return {"status": "started", **scanner.get_status()}


async def stop_scanner(api_key_id: int) -> Dict:
    """Stop a scanner for an API key"""
    if api_key_id not in _active_scanners:
        return {"status": "not_found", "message": "No scanner running for this API key"}

    scanner = _active_scanners[api_key_id]
    await scanner.stop()
    del _active_scanners[api_key_id]
    return {"status": "stopped"}


def get_scanner_status(api_key_id: int) -> Dict:
    """Get status of a scanner"""
    if api_key_id not in _active_scanners:
        return {"running": False, "message": "No scanner for this API key"}
    return _active_scanners[api_key_id].get_status()


def get_all_scanners_status() -> List[Dict]:
    """Get status of all active scanners"""
    return [scanner.get_status() for scanner in _active_scanners.values()]


async def stop_all_scanners():
    """Stop all running scanners (used during shutdown)"""
    for api_key_id in list(_active_scanners.keys()):
        await stop_scanner(api_key_id)
