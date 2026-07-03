# Trading Bot - Binance Futures Testnet

A Python trading bot for Binance Futures Testnet that places market/limit orders and executes a grid trading strategy, with structured logging and error handling.

## Features

### Core Requirements ✅
- **Order Types**: MARKET and LIMIT orders on USDT-M Futures
- **Order Sides**: BUY and SELL support
- **CLI Interface**: Command-line interface using Click
- **Input Validation**: Validates all parameters before API calls
- **Error Handling**: Handles API errors, network failures, invalid input
- **Logging**: Logs all requests, responses, and errors to file and console
- **Structured Code**: Modular architecture — separate client, orders, and validation layers

### Bonus Feature: Grid Trading 🌟
Grid trading places multiple orders across a price range instead of betting on a single direction, so it captures profit from price movement in either direction.

**Example:**
```
BTC Price Range: $40,000 - $42,000
Grid Levels: 5
Orders placed at: $40,000, $40,500, $41,000, $41,500, $42,000
```

**Implementation:**
- Calculates evenly-spaced price levels across a user-defined range
- Places all orders with proportional quantity distribution
- Continues placing remaining orders if one fails, and reports which failed
- Logs every grid order individually

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py                 # Package initialization
│   ├── client.py                   # Binance API wrapper with HMAC signing
│   ├── orders.py                   # Order placement logic (market/limit/grid)
│   ├── validators.py               # Input validation for all parameters
│   ├── response_handler.py         # Format & display API responses
│   └── logging_config.py           # Logging setup (file + console)
├── cli.py                          # Main CLI entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Template for API credentials
├── .gitignore                      # Git configuration
└── README.md                       # This file

logs/
└── trading_bot.log                 # Generated log file
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.7+
- pip (Python package manager)
- Binance Futures Testnet account

### 2. Create Binance Futures Testnet Account
1. Go to: https://testnet.binancefuture.com
2. Register for a new account
3. Verify email (coins are auto-deposited for testing)
4. Navigate to API Management
5. Create API Key and Secret
6. Keep these credentials safe — never commit to version control

### 3. Clone and Install

```bash
git clone <repository_url>
cd trading_bot

# Create virtual environment (recommended)
python -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure API Credentials

```bash
cp .env.example .env
```

Edit `.env` and add your Binance Futures Testnet API credentials:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

⚠️ **Never commit `.env` to version control** — it contains sensitive credentials.

### 5. Test Connection

```bash
python cli.py test-connection
```

Expected output:
```
Testing connection to Binance Futures Testnet...
✅ Connection Successful!
```

---

## Usage Examples

### 1. Place a MARKET Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 1
```

Output includes: order request summary, order ID, status, executed quantity, average price, and success/failure message. All details are logged to `logs/trading_bot.log`.

### 2. Place a LIMIT Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --order-type LIMIT \
  --quantity 1.5 \
  --price 43000
```

Limit orders remain on the order book (status `NEW`) until filled or cancelled — they don't execute immediately like market orders.

### 3. Grid Trading Strategy ⭐

```bash
python cli.py grid-trading \
  --symbol BTCUSDT \
  --side BUY \
  --lower-price 40000 \
  --upper-price 42000 \
  --grid-levels 5 \
  --total-qty 1.0
```

This places 5 LIMIT orders evenly spaced between $40,000–$42,000, splits the total quantity across them, and displays a summary of successful/failed orders.

---

## Logging

Example log output from `logs/trading_bot.log`:

```
2024-01-15 10:30:45 | INFO | bot.client | Binance client initialized for https://testnet.binancefuture.com
2024-01-15 10:30:46 | INFO | bot.validators | Input validation passed for MARKET BUY 1.0 BTCUSDT
2024-01-15 10:30:47 | INFO | bot.client | REQUEST: POST /fapi/v1/order params={'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 1.0}
2024-01-15 10:30:48 | INFO | bot.client | RESPONSE: status=200 data={'orderId': 12345, 'status': 'FILLED', 'executedQty': '1.0'}
2024-01-15 10:30:48 | INFO | bot.orders | Market order placed successfully: ID 12345
```

**Log includes:** every API request and response, input validation results, all errors/exceptions, order confirmations, and grid trading progress.

**Log file location:** `logs/trading_bot.log`
**Log level:** INFO (key events only — not excessive verbosity)

---

## Input Validation

| Parameter | Validation |
|-----------|-----------|
| Symbol | Must be a USDT pair (e.g., BTCUSDT) |
| Side | Must be BUY or SELL |
| Order Type | Must be MARKET or LIMIT |
| Quantity | Must be positive, between 0.001 – 10,000 |
| Price | Required for LIMIT; must be positive, between $0.01 – $1,000,000 |
| Grid Levels | Must be 3–20 |
| Price Range | Upper must exceed lower by at least 0.1% |

**Examples:**

```bash
# Missing price for LIMIT order
python cli.py place-order --symbol BTCUSDT --side BUY --order-type LIMIT --quantity 1
# Error: Price is required for LIMIT orders

# Invalid quantity
python cli.py place-order --symbol BTCUSDT --side BUY --order-type MARKET --quantity -1
# Error: Quantity must be positive
```

---

## Error Handling

- **Network errors** (timeout, connection refused, server unreachable) → logged with a clear message shown to the user
- **API errors** (invalid signature, insufficient balance, bad symbol) → Binance error code/message logged and surfaced to the user
- **Validation errors** → caught before any API call is made, saving API quota

---

## Architecture

- **`cli.py`** — entry point; orchestrates validation → order placement → response display
- **`bot/validators.py`** — validates all inputs before API calls, catches errors early
- **`bot/orders.py`** — business logic for order placement (market/limit/grid)
- **`bot/client.py`** — low-level HTTP communication, HMAC-SHA256 signature generation, request/response logging
- **`bot/response_handler.py`** — parses and formats API responses for display
- **`bot/logging_config.py`** — logging setup for file and console output

---

## Assumptions

1. **Testnet only** — uses `testnet.binancefuture.com`; switching to live trading would require changing the base URL in `client.py`
2. **USDT-M Futures only** — not compatible with COIN-M futures (e.g., BTCUSDT, ETHUSDT, BNBUSDT)
3. **API keys need Futures permission** — spot trading keys won't work
4. **Minimum order sizes** — the bot validates input ranges but does not fetch each pair's live minimum notional (would require an extra API call)
5. **No automatic order cancellation** — limit orders remain open until manually filled/cancelled; there's no timeout logic

---

## Troubleshooting

**Connection error:**
1. Check internet connection and that `testnet.binancefuture.com` is reachable
2. Verify API key/secret in `.env`
3. Run `python cli.py test-connection`

**Invalid API key (`-1022 Signature invalid`):**
1. Re-check credentials in `.env` for typos/extra spaces
2. Confirm the API key has "Futures" permission enabled
3. Regenerate the key if needed

**Grid not placing all orders:**
1. Check `logs/trading_bot.log` for the specific failure per order
2. Could be rate limiting (retry later) or insufficient testnet balance

---

## Security Considerations

1. `.env` is excluded via `.gitignore` — never commit credentials
2. Credentials are read from environment variables, not hardcoded
3. This bot is for **testnet only** and is not built for live trading without additional risk management

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| click | 8.1.7 | CLI framework |
| requests | 2.31.0 | HTTP library |
| python-dotenv | 1.0.0 | Environment variable management |
| python-binance | 1.0.17 | Optional Binance SDK (not required — using `requests` directly) |

All dependencies are pinned in `requirements.txt`.

---

## Disclaimer

⚠️ This is a **testnet** trading bot for testing purposes only, using fake USDT.
⚠️ Not intended for live trading without significant modification and risk management.
⚠️ Never share or expose real API credentials.
