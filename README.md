# Moving Average Crossover Strategy

This is a very simple Python backtester that implements a Moving Average Crossover strategy. The tool allows you to backtest different MA combinations across various time periods and stocks.

## Strategy Overview

The Moving Average Crossover is a trend-following strategy that works as follows:
- **Buy Signal**: When fast MA crosses above slow MA (bullish crossover)
- **Sell Signal**: When fast MA crosses below slow MA (bearish crossover)
- **Position**: Long when in uptrend (buy signal is 1), cash when in downtrend

## Features

- **Interactive CLI**: Customize parameters via command line arguments
- **Multiple Time Periods**: Test strategies over different durations (1m to 5y or custom dates)
- **Any Stock Symbol**: Works with any ticker available on Yahoo Finance
- **Visual Analysis**: Candlestick charts with MA overlays and equity curves
- **Data Export**: Save results to CSV for further analysis
- **Buy & Hold Comparison**: Compare strategy performance vs simple buy-and-hold

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/demetriusdemammos/crossoverStrategy.git
cd crossoverStrategy

# Install dependencies
pip install numpy pandas yfinance matplotlib mplfinance

# Create data directory
mkdir data
```

### Basic Usage

```bash
# Run with defaults (AAPL, 20/50 MA, 3 years)
python test.py

# Custom parameters
python test.py --ticker TSLA --fast 10 --slow 30 --duration 2y

# Help
python test.py --help
```

## Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--fast` | int | 20 | Fast moving average period |
| `--slow` | int | 50 | Slow moving average period |
| `--duration` | str | 3y | Time period (see options below) |
| `--ticker` | str | AAPL | Stock ticker symbol |
| `--interval` | str | 1d | Candle interval (see options below) |

### Duration Options

**Relative Periods:**
- `1d`, `7d`, `14d`, `30d` - Days
- `1m`, `3m`, `6m` - Months
- `1y`, `2y`, `3y`, `5y` - Years

**Custom Date Range:**
- `2020-01-01,2023-12-31` - Start date, End date

### Interval Options

**Intraday:**
- `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m` - Minutes
- `1h` - Hourly (same as 60m)

**Daily and Above:**
- `1d` - Daily (default)
- `5d` - 5 days
- `1wk` - Weekly  
- `1mo` - Monthly

**Note**: Intraday data has limited history (typically 60-730 days depending on the interval)

## Example Commands

```bash
# Test different MA combinations
python test.py --fast 5 --slow 15    # Faster signals
python test.py --fast 50 --slow 200  # Slower signals

# Different stocks
python test.py --ticker MSFT --duration 2y
python test.py --ticker NVDA --fast 10 --slow 25

# Custom date ranges
python test.py --duration "2020-03-01,2021-03-01"  # COVID crash recovery
python test.py --duration "2022-01-01,2023-01-01"  # Bear market year

# Different intervals
python test.py --interval 1h --duration 7d    # Hourly data for 1 week
python test.py --interval 1wk --duration 5y   # Weekly data for 5 years
python test.py --interval 5m --duration 1d    # 5-min data for 1 day
python test.py --interval 15m --duration 14d  # 15-min data for 2 weeks
```

## Output

### Console Output
```
Running MA Crossover Strategy:
Ticker: AAPL
Fast MA: 3, Slow MA: 8
Interval: 5m
Period: 2025-08-26 to 2025-08-27
--------------------------------------------------
Downloaded 78 rows of data

Strategy Performance:
Total Return: 0.55%
Final Equity: 1.0055
```

### Files Generated
- **Chart**: Interactive candlestick chart with MA overlays and equity curve
- **CSV**: `data/aapl_ma3_8_5min_1d.csv` - Full backtest data with indicators

## File Structure

```
crossoverStrategy/
- test.py          # Implementation with detailed metrics
- main.py          # Original version with more detailed analysis
- data/            # CSV exports directory
  - *.csv          # Backtest results
- README.md        # This file
```

## Key Concepts

**Moving Averages:**
- Simple Moving Average (SMA): Average price over N periods
- Smooths out price noise to identify trend direction

**Crossover Signals:**
- Bullish: Fast MA > Slow MA (uptrend)
- Bearish: Fast MA < Slow MA (downtrend)

**Execution Lag:**
- Positions taken on the bar AFTER the signal to prevent look ahead bias

## License

This project is for educational purposes. Use at your own risk for actual trading.