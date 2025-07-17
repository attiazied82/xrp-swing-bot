from entry_logic import fetch_ohlcv, check_entry_signal
from decimal import Decimal, ROUND_DOWN
import time

import pandas as pd

from ta.trend import EMAIndicator

from ta.momentum import RSIIndicator

from ta.volatility import AverageTrueRange

from binance.client import Client

import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = 'XRPEUR'  # Binance REST-API verwendet kein Slash (/)

TIMEFRAME = '4h'

EUR_PORTION = 0.8

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
   eur_balance = float(client.get_asset_balance(asset='EUR')['free'])
   amount_to_spend = eur_balance * EUR_PORTION
   raw_qty = Decimal(str(amount_to_spend / entry_price))
   # XRP erlaubt 1 Dezimalstelle → Schrittgröße 0.1
   qty = raw_qty.quantize(Decimal('0.1'), rounding=ROUND_DOWN)
   if qty < Decimal('10.0'):
       print(f"⚠️ XRP-Menge ({qty}) unter Mindestgröße (10.0). Kein Trade.")
       return
   stop = round(entry_price - 2.5 * atr, 4)
   take = round(entry_price + 3.5 * atr, 4)
   print(f"💰 EUR: {eur_balance:.2f}, Preis: {entry_price:.4f}, Kaufmenge: {qty}")
   print(f"📉 SL: {stop}, 📈 TP: {take}")
   try:
       order = client.order_market_buy(
           symbol=SYMBOL,
           quantity=str(qty)  # Binance erwartet string!
       )
       print("✅ Kauf erfolgreich:", order)
   except Exception as e:
       print("❌ Binance API-Fehler:", e)

def main():

    df = get_klines()

    df = get_indicators(df)

    latest = df.iloc[-1]

    if latest['ema20'] > latest['ema50'] and latest['rsi'] > 50:

        print("📈 Entry signal detected.")

        place_trade(latest['close'], latest['atr'])

    else:

        print("❌ No entry signal.")

if __name__ == "__main__":

    while True:

        try:

            main()

        except Exception as e:

            print("❌ Fehler:", e)

        print("⏳ Warte 60 Minuten...\n")

        time.sleep(3600)
 
