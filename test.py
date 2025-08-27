import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import argparse
from datetime import datetime, timedelta

# Global variables (will be set by command line args)
TICKER = "AAPL"

## DATA CLEANING AND VALIDATION

def validate_data(dataFrame):
    # iterate as Series rows
    for _, row in dataFrame.iterrows():
        o, h, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
        if (o < 0) or (h < 0) or (l < 0) or (c < 0):
            return False
        if not (l <= o <= h and l <= c <= h):
            return False
    return True

## ADDING INDICATORS, SIGNAL, RETURNS TO DATAFRAME
def add_indicators(px, fast=20, slow=50):
    FAST, SLOW = fast, slow
    px['EMA_{FAST}'] = px['Close'].ewm(span=FAST).mean()
    px['EMA_{SLOW}'] = px['Close'].ewm(span=SLOW).mean()
    px[f"SMA_{FAST}"] = px['Close'].rolling(FAST).mean()
    px[f"SMA_{SLOW}"] = px['Close'].rolling(SLOW).mean()
    return px

def make_position(signal):
    pos = signal.shift(1).fillna(0.0)
    return pos

def add_crossover_signal_and_position(px, fast=20, slow=50):
    FAST, SLOW = fast, slow
    px['signal'] = (px[f"SMA_{FAST}"] > px[f"SMA_{SLOW}"]).astype(int)
    px['position'] = make_position(px['signal'])
    return px

def add_returns(px):
    px['ret'] = px['Close'].pct_change().fillna(0.0)
    px['strategy_ret'] = px['position'] * px['ret']
    px['equity'] = (1 + px['strategy_ret']).cumprod()
    return px

## BACKTESTING
def backtest(df, fast=20, slow=50):
    px = df[['Open','High','Low','Close','Volume']].copy()
    FAST, SLOW = fast, slow

    px = add_indicators(px, FAST, SLOW)
    px = add_crossover_signal_and_position(px, FAST, SLOW)
    px = add_returns(px)

    return px

## PLOTTING
def plot_candles(ax, df, width=None):
    # Manually draw wicks + bodies; index must be datetime-like
    x = mdates.date2num(df.index.to_pydatetime())
    
    # Auto-calculate width based on data frequency
    if width is None and len(x) > 1:
        avg_gap = (x[-1] - x[0]) / len(x)
        width = avg_gap * 0.3  
    elif width is None:
        width = 0.3  
    
    for i, (_, row) in enumerate(df.iterrows()):
        o, h, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
        # wick
        ax.vlines(x[i], l, h, linewidth=1)
        # body
        lower = min(o, c)
        height = abs(c - o)
        color = 'green' if c >= o else 'red'
        rect = Rectangle((x[i] - width/2, lower), width, height, edgecolor=color, facecolor=color)
        ax.add_patch(rect)
    
    if len(x) > 0:
        ax.set_xlim(x[0] - width, x[-1] + width)
    ax.xaxis_date()

def plot_all(df, fast=20, slow=50, ticker="AAPL"):
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)

    # Panel 1: Price (candles) + MAs
    ax1 = fig.add_subplot(gs[0, 0])
    plot_candles(ax1, df)
    ax1.plot(df.index, df[f"SMA_{fast}"], linewidth=1.2, label=f"SMA {fast}")
    ax1.plot(df.index, df[f"SMA_{slow}"], linewidth=1.2, label=f"SMA {slow}")
    ax1.set_title(f"{ticker} | {fast}/{slow} MA Crossover")
    ax1.set_ylabel("Price")
    ax1.legend(loc='best')
    ax1.grid(True)
    
    # Set x-axis limits to actual data range
    ax1.set_xlim(df.index[0], df.index[-1])
    
    # Panel 2: Equity curve
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)
    ax2.plot(df.index, df['equity'], linewidth=1.2, label='Strategy')
    ax2.set_ylabel("Equity")
    ax2.legend(loc='best')
    ax2.grid(True)
    
    # Set x-axis limits to actual data range
    ax2.set_xlim(df.index[0], df.index[-1])
    
    plt.tight_layout()
    plt.show()

def parse_args():
    parser = argparse.ArgumentParser(description='MA Crossover Strategy Backtester')
    parser.add_argument('--fast', type=int, default=20, help='Fast moving average period (default: 20)')
    parser.add_argument('--slow', type=int, default=50, help='Slow moving average period (default: 50)')
    parser.add_argument('--duration', type=str, default='3y', 
                       help='Duration: 7d, 14d, 30d, 1m, 3m, 6m, 1y, 2y, 3y, 5y, or YYYY-MM-DD,YYYY-MM-DD (default: 3y)')
    parser.add_argument('--ticker', type=str, default='AAPL', help='Stock ticker (default: AAPL)')
    parser.add_argument('--interval', type=str, default='1d', 
                       help='Candle interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo (default: 1d)')
    return parser.parse_args()

def parse_duration(duration_str):
    """Parse duration string into start and end dates"""
    today = datetime.now()
    
    if ',' in duration_str:
        # Custom date range: "2022-01-01,2025-01-01"
        start_str, end_str = duration_str.split(',')
        return start_str.strip(), end_str.strip()
    
    # Relative durations
    duration_map = {
        '1d': timedelta(days=1),
        '7d': timedelta(days=7),
        '14d': timedelta(days=14),
        '30d': timedelta(days=30),
        '1m': timedelta(days=30),
        '3m': timedelta(days=90),
        '6m': timedelta(days=180),
        '1y': timedelta(days=365),
        '2y': timedelta(days=730),
        '3y': timedelta(days=1095),
        '5y': timedelta(days=1825)
    }
    
    if duration_str in duration_map:
        start_date = today - duration_map[duration_str]
        return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    else:
        raise ValueError(f"Invalid duration: {duration_str}. Use 7d, 14d, 30d, 1m, 3m, 6m, 1y, 2y, 3y, 5y, or YYYY-MM-DD,YYYY-MM-DD")

## MAIN
def main():
    args = parse_args()
    
    # Parse duration
    start_date, end_date = parse_duration(args.duration)
    
    print(f"Running MA Crossover Strategy:")
    print(f"Ticker: {args.ticker}")
    print(f"Fast MA: {args.fast}, Slow MA: {args.slow}")
    print(f"Interval: {args.interval}")
    print(f"Period: {start_date} to {end_date}")
    print("-" * 50)
    
    # Download data
    df = yf.download(args.ticker, start=start_date, end=end_date, interval=args.interval, auto_adjust=True)
    df = df.dropna()
    
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.droplevel(-1)
    
    print(f"Downloaded {len(df)} rows of data")
    
    # Run backtest
    px = backtest(df, args.fast, args.slow)
    
    # Plot results
    plot_all(px, args.fast, args.slow, args.ticker)
    
    # Save to CSV
    interval_clean = args.interval.replace('m', 'min').replace('h', 'hr').replace('d', 'day').replace('wk', 'week').replace('mo', 'month')
    filename = f'data/{args.ticker.lower()}_ma{args.fast}_{args.slow}_{interval_clean}_{args.duration.replace(",", "_")}.csv'
    px.to_csv(filename)
    print(f"\nData saved to {filename} ({len(px)} rows)")
    
    # Print basic stats
    final_equity = px['equity'].iloc[-1]
    total_return = (final_equity - 1) * 100
    print(f"\nStrategy Performance:")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Final Equity: {final_equity:.4f}")

if __name__ == "__main__":
    main()