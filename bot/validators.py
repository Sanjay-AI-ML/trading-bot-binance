"""
Input Validation Module
Validates all user inputs before sending to Binance API
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Common trading pairs on Binance Futures
COMMON_SYMBOLS = {
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
    'DOGEUSDT', 'LTCUSDT', 'TRXUSDT', 'AVAXUSDT', 'LINKUSDT',
    'UNIUSDT', 'MATICUSDT', 'SUSHIUSDT', 'ATOMUSDT', 'SOLGRAM',
}

# Minimum order quantities (example values - adjust per symbol if needed)
MIN_QUANTITY = 0.001
MAX_QUANTITY = 10000

# Price constraints
MIN_PRICE = 0.01
MAX_PRICE = 1000000


class InputValidator:
    """
    Validates all user inputs for order placement
    Catches errors early before API calls
    """
    
    def __init__(self):
        logger.info("InputValidator initialized")
    
    def validate_symbol(self, symbol: str) -> Tuple[bool, str]:
        """
        Validate trading pair symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            (is_valid, error_message)
        """
        symbol = symbol.upper()
        
        if not symbol:
            return False, "Symbol cannot be empty"
        
        if len(symbol) < 6:
            return False, f"Symbol '{symbol}' is too short (minimum 6 characters)"
        
        if not symbol.endswith('USDT'):
            return False, f"Symbol '{symbol}' must be a USDT pair (e.g., BTCUSDT)"
        
        # Warn if not in common symbols (but still allow it)
        if symbol not in COMMON_SYMBOLS:
            logger.warning(f"Symbol '{symbol}' is not in common list, proceeding anyway")
        
        return True, ""
    
    def validate_side(self, side: str) -> Tuple[bool, str]:
        """
        Validate order side (BUY/SELL)
        
        Args:
            side: 'BUY' or 'SELL'
            
        Returns:
            (is_valid, error_message)
        """
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            return False, f"Side must be 'BUY' or 'SELL', got '{side}'"
        
        return True, ""
    
    def validate_order_type(self, order_type: str) -> Tuple[bool, str]:
        """
        Validate order type
        
        Args:
            order_type: 'MARKET', 'LIMIT', 'STOP_LIMIT', etc.
            
        Returns:
            (is_valid, error_message)
        """
        order_type = order_type.upper()
        
        valid_types = ['MARKET', 'LIMIT', 'STOP_LIMIT', 'STOP', 'TRAILING_STOP_MARKET']
        
        if order_type not in valid_types:
            return False, f"Order type must be one of {valid_types}, got '{order_type}'"
        
        return True, ""
    
    def validate_quantity(self, quantity: float) -> Tuple[bool, str]:
        """
        Validate order quantity
        
        Args:
            quantity: Order quantity
            
        Returns:
            (is_valid, error_message)
        """
        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            return False, f"Quantity must be a number, got '{quantity}'"
        
        if quantity <= 0:
            return False, f"Quantity must be positive, got {quantity}"
        
        if quantity < MIN_QUANTITY:
            return False, f"Quantity too small (minimum: {MIN_QUANTITY})"
        
        if quantity > MAX_QUANTITY:
            return False, f"Quantity too large (maximum: {MAX_QUANTITY})"
        
        # Check decimal places (typically max 8 for crypto)
        if len(str(quantity).split('.')[-1]) > 8:
            return False, f"Quantity has too many decimal places (maximum 8)"
        
        return True, ""
    
    def validate_price(self, price: float) -> Tuple[bool, str]:
        """
        Validate price
        
        Args:
            price: Order price
            
        Returns:
            (is_valid, error_message)
        """
        try:
            price = float(price)
        except (TypeError, ValueError):
            return False, f"Price must be a number, got '{price}'"
        
        if price <= 0:
            return False, f"Price must be positive, got {price}"
        
        if price < MIN_PRICE:
            return False, f"Price too low (minimum: ${MIN_PRICE})"
        
        if price > MAX_PRICE:
            return False, f"Price too high (maximum: ${MAX_PRICE})"
        
        return True, ""
    
    def validate_order_input(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None
    ) -> Tuple[bool, str]:
        """
        Validate complete order input
        
        Args:
            symbol: Trading pair
            side: BUY/SELL
            order_type: MARKET/LIMIT
            quantity: Order quantity
            price: Price (required for LIMIT orders)
            
        Returns:
            (is_valid, error_message)
        """
        # Validate symbol
        is_valid, msg = self.validate_symbol(symbol)
        if not is_valid:
            return False, msg
        
        # Validate side
        is_valid, msg = self.validate_side(side)
        if not is_valid:
            return False, msg
        
        # Validate order type
        is_valid, msg = self.validate_order_type(order_type)
        if not is_valid:
            return False, msg
        
        # Validate quantity
        is_valid, msg = self.validate_quantity(quantity)
        if not is_valid:
            return False, msg
        
        # Validate price for LIMIT orders
        if order_type.upper() in ['LIMIT', 'STOP_LIMIT']:
            if price is None:
                return False, f"Price is required for {order_type} orders"
            
            is_valid, msg = self.validate_price(price)
            if not is_valid:
                return False, msg
        
        logger.info(f"Input validation passed for {order_type} {side} {quantity} {symbol}")
        return True, ""
    
    def validate_grid_input(
        self,
        symbol: str,
        side: str,
        lower_price: float,
        upper_price: float
    ) -> Tuple[bool, str]:
        """
        Validate grid trading input
        
        Args:
            symbol: Trading pair
            side: BUY/SELL
            lower_price: Grid lower bound
            upper_price: Grid upper bound
            
        Returns:
            (is_valid, error_message)
        """
        # Validate symbol
        is_valid, msg = self.validate_symbol(symbol)
        if not is_valid:
            return False, msg
        
        # Validate side
        is_valid, msg = self.validate_side(side)
        if not is_valid:
            return False, msg
        
        # Validate prices
        is_valid, msg = self.validate_price(lower_price)
        if not is_valid:
            return False, f"Lower price invalid: {msg}"
        
        is_valid, msg = self.validate_price(upper_price)
        if not is_valid:
            return False, f"Upper price invalid: {msg}"
        
        if lower_price >= upper_price:
            return False, f"Lower price (${lower_price}) must be less than upper price (${upper_price})"
        
        # Price range shouldn't be too tight
        price_diff = upper_price - lower_price
        min_range = lower_price * 0.001  # At least 0.1% difference
        
        if price_diff < min_range:
            return False, f"Price range too tight (minimum {min_range:.2f} difference)"
        
        logger.info(f"Grid input validation passed for {symbol} ${lower_price}-${upper_price}")
        return True, ""
