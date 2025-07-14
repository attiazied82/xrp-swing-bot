
import time
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from binance.client import Client

API_KEY = '5huWOQsBrwBCFPTL6YBPxzpV0pCZHx5nd9qDm9MB5CHngY2OCglQmlDlsqBBE0VV'
API_SECRET = '0uaiZXnDF5S1k17kz3DPRla4XSisTVYHZ7qvuQ9Bb4WVwsDhNdbv2Pad6xzXAuc0'

client = Client(API_KEY, API_SECRET)

SYMBOL = 'XRPUSDT'
TIMEFRAME = '4h'
USDT_PORTION = 0.8

def get_klines():
    klines = client.get_klines(symbol=SYMBOL, interval=TIMEFRAME, limit=100)
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'num_trades', 'tbb', 'tbq', 'ignore'
    ])
    df = df.astype({'open':'float','high':'float','low':'float','close':'float'})
    return df

def get_indicators(df):
    df['ema20'] = EMAIndicator(df['close'], 20).ema_indicator()
    df['ema50'] = EMAIndicator(df['close'], 50).ema_indicator()
    df['rsi'] = RSIIndicator(df['close'], 14).rsi()
    df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], 14).average_true_range()
    return df

def place_trade(entry_price, atr):
    usdt_balance = float(client.get_asset_balance('USDT')['free'])
    qty = (usdt_balance * USDT_PORTION) / entry_price
    stop = round(entry_price - 1.5 * atr, 4)
    take = round(entry_price + 2.5 * atr, 4)

    order = client.order_market_buy(symbol=SYMBOL, quantity=round(qty, 1))
    print("Buy order executed:", order)
    print(f"SL set to {stop}, TP set to {take}")

def main():
    df = get_klines()
    df = get_indicators(df)
    latest = df.iloc[-1]
    if latest['ema20'] > latest['ema50'] and latest['rsi'] > 50:
        print("Entry signal detected.")
        place_trade(latest['close'], latest['atr'])
    else:
        print("No signal.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Error:", e)
        time.sleep(3600)
