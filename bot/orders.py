"""
Order Management Module
Handles order placement logic and validation
"""

import logging
from typing import Optional, Dict
from bot.client import BinanceClient

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Manages order placement on Binance Futures
    Handles MARKET and LIMIT orders with error handling
    """
    
    def __init__(self, client: BinanceClient):
        """
        Initialize OrderManager
        
        Args:
            client: BinanceClient instance
        """
        self.client = client
        logger.info("OrderManager initialized")
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Optional[Dict]:
        """
        Place a MARKET order
        
        Market orders execute immediately at the best available price.
        No price parameter needed.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            
        Returns:
            Order response with orderId, status, executedQty, etc.
        """
        try:
            logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
            
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=quantity,
                price=None
            )
            
            # Check for errors
            if response is None:
                logger.error("Market order returned None response")
                return {'code': -1, 'msg': 'No response from server'}
            
            if 'code' in response and response['code'] != 0:
                logger.error(f"Market order failed: {response}")
                return response
            
            if 'orderId' in response:
                logger.info(f"Market order placed successfully: ID {response['orderId']}")
                return response
            else:
                logger.error(f"Unexpected response format: {response}")
                return response
        
        except Exception as e:
            error_msg = f"Exception in place_market_order: {str(e)}"
            logger.error(error_msg)
            return {'code': -1, 'msg': error_msg}
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC'
    ) -> Optional[Dict]:
        """
        Place a LIMIT order
        
        Limit orders execute only at the specified price or better.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            time_in_force: 'GTC' (Good Till Cancel), 'IOC' (Immediate or Cancel), 'FOK' (Fill or Kill)
            
        Returns:
            Order response with orderId, status, etc.
        """
        try:
            if price <= 0:
                error_msg = "Price must be greater than 0"
                logger.error(error_msg)
                return {'code': -1000, 'msg': error_msg}
            
            if quantity <= 0:
                error_msg = "Quantity must be greater than 0"
                logger.error(error_msg)
                return {'code': -1000, 'msg': error_msg}
            
            logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ ${price}")
            
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type='LIMIT',
                quantity=quantity,
                price=price,
                time_in_force=time_in_force
            )
            
            # Check for errors
            if response is None:
                logger.error("Limit order returned None response")
                return {'code': -1, 'msg': 'No response from server'}
            
            if 'code' in response and response['code'] != 0:
                logger.error(f"Limit order failed: {response}")
                return response
            
            if 'orderId' in response:
                logger.info(f"Limit order placed successfully: ID {response['orderId']}")
                return response
            else:
                logger.error(f"Unexpected response format: {response}")
                return response
        
        except Exception as e:
            error_msg = f"Exception in place_limit_order: {str(e)}"
            logger.error(error_msg)
            return {'code': -1, 'msg': error_msg}
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        price: float
    ) -> Optional[Dict]:
        """
        Place a STOP_LIMIT order (bonus feature)
        
        Stop-limit orders trigger when price hits stop_price, then execute as limit order.
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            stop_price: Trigger price
            price: Limit price (after trigger)
            
        Returns:
            Order response
        """
        try:
            logger.info(f"Placing STOP_LIMIT order: {side} {quantity} {symbol} stop={stop_price} limit={price}")
            
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'STOP_LIMIT',
                'quantity': quantity,
                'price': price,
                'stopPrice': stop_price,
                'timeInForce': 'GTC'
            }
            
            response = self.client._send_request(
                method='POST',
                endpoint='/fapi/v1/order',
                params=params,
                signed=True
            )
            
            if response and 'orderId' in response:
                logger.info(f"Stop-limit order placed: ID {response['orderId']}")
            
            return response
        
        except Exception as e:
            logger.error(f"Stop-limit order error: {str(e)}")
            return {'code': -1, 'msg': str(e)}
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Check order status
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order details
        """
        try:
            response = self.client.get_order_status(symbol, order_id)
            return response
        
        except Exception as e:
            logger.error(f"Error checking order status: {str(e)}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Cancel an order
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Cancel response
        """
        try:
            response = self.client.cancel_order(symbol, order_id)
            if response and 'orderId' in response:
                logger.info(f"Order {order_id} cancelled successfully")
            return response
        
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return None
