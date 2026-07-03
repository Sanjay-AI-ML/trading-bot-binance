"""
Binance Futures Testnet API Client
Handles authentication, request signing, and HTTP communication
"""

import hmac
import hashlib
import time
import requests
from typing import Dict, Optional
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """
    Wrapper for Binance Futures Testnet API
    Handles HMAC-SHA256 signing and request routing
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        """
        Initialize Binance client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            base_url: Testnet base URL (default: testnet.binancefuture.com)
        """
        if not api_key or not api_secret:
            logger.error("API key and secret are required")
            raise ValueError("API key and secret must be provided")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
        
        logger.info(f"Binance client initialized for {base_url}")
    
    def _generate_signature(self, params: Dict) -> str:
        """
        Generate HMAC-SHA256 signature for request
        
        Args:
            params: Query parameters
            
        Returns:
            HMAC-SHA256 signature
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        signed: bool = True
    ) -> Optional[Dict]:
        """
        Send HTTP request to Binance API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/fapi/v1/order')
            params: Request parameters
            signed: Whether request requires signing
            
        Returns:
            JSON response or None if error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            if params is None:
                params = {}
            
            # Add timestamp for signed requests
            if signed:
                params['timestamp'] = int(time.time() * 1000)
                params['recvWindow'] = 5000
                params['signature'] = self._generate_signature(params)
            
            logger.info(f"REQUEST: {method} {endpoint} params={params}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"RESPONSE: status={response.status_code} data={data}")
            return data
        
        except requests.exceptions.Timeout:
            error_msg = "Request timeout - network connection issue"
            logger.error(error_msg)
            return {'code': -1001, 'msg': error_msg}
        
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error - unable to reach Binance servers"
            logger.error(error_msg)
            return {'code': -1000, 'msg': error_msg}
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            try:
                return e.response.json()
            except:
                return {'code': e.response.status_code, 'msg': error_msg}
        
        except Exception as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return {'code': -1, 'msg': error_msg}
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = 'GTC'
    ) -> Optional[Dict]:
        """
        Place an order on Binance Futures
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            order_type: 'MARKET' or 'LIMIT'
            quantity: Order quantity
            price: Price (required for LIMIT orders)
            time_in_force: 'GTC', 'IOC', 'FOK' (default: GTC = Good Till Cancelled)
            
        Returns:
            Order response or None if error
        """
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity
            }
            
            if order_type.upper() == 'LIMIT':
                if price is None:
                    raise ValueError("Price is required for LIMIT orders")
                params['price'] = price
                params['timeInForce'] = time_in_force
            
            logger.info(f"Placing {order_type} order: {params}")
            
            response = self._send_request(
                method='POST',
                endpoint='/fapi/v1/order',
                params=params,
                signed=True
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {'code': -1, 'msg': str(e)}
    
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Cancel an existing order
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
            
        Returns:
            Cancel response
        """
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            logger.info(f"Cancelling order {order_id} for {symbol}")
            
            response = self._send_request(
                method='DELETE',
                endpoint='/fapi/v1/order',
                params=params,
                signed=True
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return {'code': -1, 'msg': str(e)}
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Get status of an order
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order details
        """
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            
            response = self._send_request(
                method='GET',
                endpoint='/fapi/v1/order',
                params=params,
                signed=True
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return None
    
    def get_server_time(self) -> Optional[Dict]:
        """
        Get server time (useful for connectivity test)
        
        Returns:
            Server time response
        """
        try:
            response = self._send_request(
                method='GET',
                endpoint='/fapi/v1/time',
                signed=False
            )
            return response
        
        except Exception as e:
            logger.error(f"Error getting server time: {str(e)}")
            return None
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("Binance client session closed")
