#!/usr/bin/env python3
"""
Trading Bot CLI - Binance Futures Testnet
Main entry point for placing orders and grid trading
"""

import sys
import os
from pathlib import Path
import click
from dotenv import load_dotenv

# Add bot module to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.client import BinanceClient
from bot.orders import OrderManager
from bot.validators import InputValidator
from bot.response_handler import ResponseHandler
from bot.logging_config import setup_logging

# Load environment variables
load_dotenv()
logger = setup_logging()


@click.group()
def cli():
    """Trading Bot - Binance Futures Testnet Order Placement"""
    pass


@cli.command()
@click.option('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL'], case_sensitive=False), help='Order side')
@click.option('--quantity', required=True, type=float, help='Order quantity')
@click.option('--price', type=float, default=None, help='Price (required for LIMIT orders)')
@click.option('--order-type', required=True, type=click.Choice(['MARKET', 'LIMIT'], case_sensitive=False), help='Order type')
def place_order(symbol, side, quantity, price, order_type):
    """Place a single MARKET or LIMIT order on Binance Futures Testnet"""
    
    try:
        # Validate input
        symbol = symbol.upper()
        side = side.upper()
        order_type = order_type.upper()
        
        validator = InputValidator()
        is_valid, error_msg = validator.validate_order_input(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        if not is_valid:
            click.secho(f"❌ Validation Error: {error_msg}", fg='red', bold=True)
            logger.error(f"Validation failed: {error_msg}")
            sys.exit(1)
        
        # Initialize client and order manager
        client = BinanceClient(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_API_SECRET')
        )
        order_manager = OrderManager(client)
        response_handler = ResponseHandler()
        
        # Log order request
        logger.info(f"Placing {order_type} order: {side} {quantity} {symbol} @ {price if price else 'market price'}")
        
        # Place order
        if order_type == 'MARKET':
            response = order_manager.place_market_order(symbol, side, quantity)
        else:  # LIMIT
            response = order_manager.place_limit_order(symbol, side, quantity, price)
        
        # Handle and display response
        if response and 'orderId' in response:
            click.secho("✅ Order Placed Successfully!", fg='green', bold=True)
            response_handler.display_order_response(response)
            logger.info(f"Order placed successfully: {response['orderId']}")
        else:
            click.secho("❌ Order Failed!", fg='red', bold=True)
            logger.error(f"Order failed: {response}")
            if response and 'msg' in response:
                click.secho(f"Error: {response['msg']}", fg='yellow')
    
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg='red', bold=True)
        logger.exception(f"Exception during order placement: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
@click.option('--side', required=True, type=click.Choice(['BUY', 'SELL'], case_sensitive=False), help='Grid side')
@click.option('--lower-price', required=True, type=float, help='Lower price bound')
@click.option('--upper-price', required=True, type=float, help='Upper price bound')
@click.option('--grid-levels', required=True, type=int, help='Number of grid levels (3-20)')
@click.option('--total-qty', required=True, type=float, help='Total quantity across all levels')
def grid_trading(symbol, side, lower_price, upper_price, grid_levels, total_qty):
    """
    Place a grid of orders across a price range
    
    Example:
    python cli.py grid-trading --symbol BTCUSDT --side BUY --lower-price 40000 --upper-price 42000 --grid-levels 5 --total-qty 1.0
    """
    
    try:
        # Validate inputs
        symbol = symbol.upper()
        side = side.upper()
        
        if grid_levels < 3 or grid_levels > 20:
            click.secho("❌ Grid levels must be between 3 and 20", fg='red', bold=True)
            sys.exit(1)
        
        if lower_price >= upper_price:
            click.secho("❌ Lower price must be less than upper price", fg='red', bold=True)
            sys.exit(1)
        
        if total_qty <= 0:
            click.secho("❌ Total quantity must be greater than 0", fg='red', bold=True)
            sys.exit(1)
        
        validator = InputValidator()
        is_valid, error_msg = validator.validate_grid_input(symbol, side, lower_price, upper_price)
        
        if not is_valid:
            click.secho(f"❌ Validation Error: {error_msg}", fg='red', bold=True)
            logger.error(f"Grid validation failed: {error_msg}")
            sys.exit(1)
        
        # Initialize client and order manager
        client = BinanceClient(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_API_SECRET')
        )
        order_manager = OrderManager(client)
        response_handler = ResponseHandler()
        
        # Calculate grid levels
        price_step = (upper_price - lower_price) / (grid_levels - 1)
        qty_per_level = total_qty / grid_levels
        
        click.secho(f"\n📊 Grid Trading Configuration", fg='cyan', bold=True)
        click.secho(f"Symbol: {symbol} | Side: {side}", fg='white')
        click.secho(f"Price Range: ${lower_price:,.2f} - ${upper_price:,.2f}", fg='white')
        click.secho(f"Grid Levels: {grid_levels} | Qty/Level: {qty_per_level:.8f}", fg='white')
        click.secho(f"Total Quantity: {total_qty} | Price Step: ${price_step:,.2f}\n", fg='white')
        
        # Place grid orders
        logger.info(f"Starting grid trading: {symbol} {side} {grid_levels} levels ${lower_price}-${upper_price}")
        
        order_ids = []
        successful_orders = 0
        failed_orders = 0
        
        with click.progressbar(range(grid_levels), label='Placing orders') as bar:
            for i in bar:
                try:
                    price = lower_price + (i * price_step)
                    price = round(price, 2)  # Round to 2 decimals
                    
                    response = order_manager.place_limit_order(
                        symbol=symbol,
                        side=side,
                        quantity=qty_per_level,
                        price=price
                    )
                    
                    if response and 'orderId' in response:
                        order_ids.append(response['orderId'])
                        successful_orders += 1
                        logger.info(f"Grid order {i+1}/{grid_levels} placed: ID {response['orderId']} @ ${price}")
                    else:
                        failed_orders += 1
                        logger.error(f"Grid order {i+1} failed at ${price}: {response}")
                
                except Exception as e:
                    failed_orders += 1
                    logger.error(f"Grid order {i+1} exception: {str(e)}")
        
        # Display summary
        click.secho(f"\n📈 Grid Trading Summary", fg='cyan', bold=True)
        click.secho(f"✅ Successful Orders: {successful_orders}/{grid_levels}", fg='green')
        if failed_orders > 0:
            click.secho(f"❌ Failed Orders: {failed_orders}/{grid_levels}", fg='red')
        click.secho(f"Order IDs: {order_ids}\n", fg='white')
        
        logger.info(f"Grid trading completed: {successful_orders} placed, {failed_orders} failed")
        
    except Exception as e:
        click.secho(f"❌ Grid Trading Error: {str(e)}", fg='red', bold=True)
        logger.exception(f"Grid trading exception: {str(e)}")
        sys.exit(1)


@cli.command()
def test_connection():
    """Test connection to Binance Futures Testnet"""
    
    try:
        click.secho("Testing connection to Binance Futures Testnet...", fg='cyan')
        
        client = BinanceClient(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_API_SECRET')
        )
        
        # Try to get server time
        response = client.get_server_time()
        
        if response:
            click.secho("✅ Connection Successful!", fg='green', bold=True)
            logger.info("Connection test successful")
        else:
            click.secho("❌ Connection Failed!", fg='red', bold=True)
            logger.error("Connection test failed")
    
    except Exception as e:
        click.secho(f"❌ Connection Error: {str(e)}", fg='red', bold=True)
        logger.error(f"Connection test error: {str(e)}")


if __name__ == '__main__':
    cli()
