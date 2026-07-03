"""
Response Handler Module
Formats and displays Binance API responses in user-friendly format
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseHandler:
    """
    Formats Binance API responses for display
    Extracts and presents key order information
    """
    
    def __init__(self):
        logger.info("ResponseHandler initialized")
    
    def display_order_response(self, response: Dict) -> None:
        """
        Display order response in formatted way
        
        Args:
            response: Binance API response
        """
        if not response:
            print("No response received")
            return
        
        if 'code' in response and response['code'] != 0:
            print(f"\n❌ Order Failed!")
            print(f"Error Code: {response.get('code')}")
            print(f"Error Message: {response.get('msg')}")
            logger.error(f"Order failed: {response}")
            return
        
        # Extract key fields
        order_id = response.get('orderId', 'N/A')
        symbol = response.get('symbol', 'N/A')
        side = response.get('side', 'N/A')
        order_type = response.get('type', 'N/A')
        status = response.get('status', 'N/A')
        quantity = response.get('origQty', response.get('quantity', 'N/A'))
        executed_qty = response.get('executedQty', 'N/A')
        price = response.get('price', response.get('avgPrice', 'N/A'))
        avg_price = response.get('avgPrice', 'N/A')
        commission = response.get('commission', 'N/A')
        timestamp = response.get('time', response.get('updateTime', 0))
        
        # Format output
        print("\n" + "="*60)
        print("📋 ORDER RESPONSE DETAILS")
        print("="*60)
        
        print(f"\n📊 Order Information:")
        print(f"   Order ID:          {order_id}")
        print(f"   Symbol:            {symbol}")
        print(f"   Side:              {side}")
        print(f"   Type:              {order_type}")
        print(f"   Status:            {status}")
        
        print(f"\n💰 Quantity & Pricing:")
        print(f"   Original Qty:      {quantity}")
        print(f"   Executed Qty:      {executed_qty}")
        print(f"   Price:             {price}")
        if avg_price and avg_price != 'N/A':
            print(f"   Average Price:     {avg_price}")
        
        if commission and commission != 'N/A':
            print(f"   Commission:        {commission}")
        
        # Timestamp
        if timestamp:
            try:
                dt = datetime.fromtimestamp(timestamp / 1000)
                print(f"\n⏰ Timestamp:        {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                pass
        
        # Additional fields if present
        if 'fills' in response and response['fills']:
            print(f"\n📈 Fills ({len(response['fills'])}):")
            for i, fill in enumerate(response['fills'], 1):
                fill_qty = fill.get('qty', 'N/A')
                fill_price = fill.get('price', 'N/A')
                fill_commission = fill.get('commission', 'N/A')
                print(f"   [{i}] {fill_qty} @ ${fill_price} (commission: {fill_commission})")
        
        print("\n" + "="*60 + "\n")
        
        logger.info(f"Order displayed: {order_id} {side} {executed_qty} {symbol}")
    
    def format_grid_response(self, responses: list) -> Dict:
        """
        Format grid trading responses
        
        Args:
            responses: List of order responses
            
        Returns:
            Formatted grid summary
        """
        successful = []
        failed = []
        
        for response in responses:
            if response and 'orderId' in response:
                successful.append(response['orderId'])
            else:
                failed.append(response)
        
        summary = {
            'total': len(responses),
            'successful': len(successful),
            'failed': len(failed),
            'order_ids': successful,
            'failed_orders': failed
        }
        
        logger.info(f"Grid summary: {summary['successful']}/{summary['total']} orders placed")
        return summary
    
    def extract_order_info(self, response: Dict) -> Dict:
        """
        Extract key order information from response
        
        Args:
            response: Binance API response
            
        Returns:
            Dictionary with key fields
        """
        if not response:
            return {}
        
        return {
            'orderId': response.get('orderId'),
            'symbol': response.get('symbol'),
            'side': response.get('side'),
            'type': response.get('type'),
            'status': response.get('status'),
            'quantity': response.get('origQty'),
            'executedQty': response.get('executedQty'),
            'price': response.get('price'),
            'avgPrice': response.get('avgPrice'),
            'commission': response.get('commission'),
            'timestamp': response.get('time')
        }
    
    def validate_response(self, response: Dict) -> tuple:
        """
        Check if response indicates success
        
        Args:
            response: API response
            
        Returns:
            (is_success, message)
        """
        if not response:
            return False, "No response"
        
        # Check for error code
        if 'code' in response and response['code'] != 0:
            msg = response.get('msg', 'Unknown error')
            return False, f"Error: {msg}"
        
        # Check for orderId (indicates success)
        if 'orderId' in response:
            status = response.get('status', 'UNKNOWN')
            return True, f"Success (Status: {status})"
        
        return False, "Invalid response format"
