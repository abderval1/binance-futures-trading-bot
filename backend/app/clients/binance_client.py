import hmac
import hashlib
import time
import json
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import httpx
from ..config import settings
from ..utils.encryption import decrypt_api_key


class BinanceFuturesClient:
    """Async Binance Futures API client"""

    BASE_URL = "https://fapi.binance.com"
    TESTNET_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key_id: int, encrypted_api_key: str, encrypted_secret: str, testnet: bool = False):
        self.api_key_id = api_key_id
        self.base_url = self.TESTNET_URL if testnet else self.BASE_URL
        self.api_key, self.secret_key = decrypt_api_key(encrypted_api_key, encrypted_secret)
        self.client = httpx.AsyncClient(timeout=30.0)

    def _sign(self, query_string: str) -> str:
        """Sign request with HMAC SHA256"""
        return hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False, data: Dict = None):
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}

        if signed:
            params = params or {}
            params["timestamp"] = int(time.time() * 1000)
            query_string = urlencode(params, doseq=True)
            signature = self._sign(query_string)
            url += f"?{query_string}&signature={signature}"

        if method.upper() == "GET":
            response = await self.client.get(url, headers=headers)
        elif method.upper() == "POST":
            response = await self.client.post(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = await self.client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()

    # ========== Account ==========
    async def get_account_info(self):
        return await self._request("GET", "/fapi/v2/account", signed=True)

    async def get_balance(self) -> List[Dict]:
        """Get futures account balance"""
        data = await self.get_account_info()
        return data.get("assets", [])

    async def get_positions(self) -> List[Dict]:
        """Get open positions"""
        data = await self.get_account_info()
        return [p for p in data.get("positions", []) if float(p.get("positionAmt", 0)) != 0]

    # ========== Orders ==========
    async def place_order(
        self,
        symbol: str,
        side: str,  # BUY or SELL
        order_type: str,  # MARKET, LIMIT, STOP, TAKE_PROFIT
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
        close_position: bool = False
    ) -> Dict:
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price:
            params["price"] = price
        if stop_price:
            params["stopPrice"] = stop_price
        if order_type != "MARKET":
            params["timeInForce"] = time_in_force
        if reduce_only:
            params["reduceOnly"] = True
        if close_position:
            params["closePosition"] = True

        return await self._request("POST", "/fapi/v1/order", params=params, signed=True)

    async def get_order(self, symbol: str, order_id: str) -> Dict:
        params = {"symbol": symbol, "orderId": order_id}
        return await self._request("GET", "/fapi/v1/order", params=params, signed=True)

    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        params = {"symbol": symbol, "orderId": order_id}
        return await self._request("DELETE", "/fapi/v1/order", params=params, signed=True)

    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/fapi/v1/openOrders", params=params, signed=True)

    # ========== Positions ==========
    async def set_leverage(self, symbol: str, leverage: int):
        params = {"symbol": symbol, "leverage": leverage}
        return await self._request("POST", "/fapi/v1/leverage", params=params, signed=True)

    async def set_margin_type(self, symbol: str, margin_type: str):
        """ISOLATED or CROSS"""
        params = {"symbol": symbol, "marginType": margin_type}
        return await self._request("POST", "/fapi/v1/marginType", params=params, signed=True)

    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        account = await self.get_account_info()
        positions = account.get("positions", [])
        return [p for p in positions if float(p.get("positionAmt", 0)) != 0]

    # ========== Market Data ==========
    async def get_ticker_price(self, symbol: str) -> float:
        resp = await self._request("GET", "/fapi/v1/ticker/24hr", params={"symbol": symbol})
        return float(resp["lastPrice"])

    async def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/fapi/v1/exchangeInfo", params=params)

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500
    ) -> List[List]:
        """Get candlestick data"""
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        return await self._request("GET", "/fapi/v1/klines", params=params)

    # ========== WebSocket (for real-time updates) ==========
    def get_ws_stream(self, streams: List[str]):
        """Get WebSocket streams for real-time data"""
        streams_str = "/".join(streams)
        return f"wss://fstream.binance.com/ws/{streams_str}"

    async def close(self):
        await self.client.aclose()
