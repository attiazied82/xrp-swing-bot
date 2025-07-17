import ccxt

import time

import datetime

import pandas as pd

# Strategieparameter

DROP_THRESHOLD = 0.97  # Preis fällt um >3 %

SMA_PERIOD = 50        # Gleitender Durchschnitt

TIMEFRAME = "10m"      # 10-Minuten-Chart

# Binance initialisieren

exchange = ccxt.binance({

    'enableRateLimit': True

})

exchange.options['defaultType'] = 'spot'

def fetch_ohlcv(symbol="XRP/EUR", limit=60):

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=limit)

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    return df

def check_entry_signal(df):

    if len(df) < SMA_PERIOD + 2:

        return False, "Nicht genug Daten für SMA"

    current_price = df.iloc[-1]["close"]

    price_prev = df.iloc[-2]["close"]

    sma = df["close"].rolling(SMA_PERIOD).mean().iloc[-1]

    if current_price < price_prev * DROP_THRESHOLD and current_price > sma:

        return True, f"Einstieg erkannt: Preis {current_price:.4f}, SMA50 {sma:.4f}"

    else:

        return False, f"Kein Einstieg: Preis {current_price:.4f}, SMA50 {sma:.4f}"

def live_loop():

    while True:

        print(f"\n⏱ {datetime.datetime.now()} – Prüfe Entry-Strategie...")

        try:

            df = fetch_ohlcv()

            signal, message = check_entry_signal(df)

            print("🔍", message)

            if signal:

                print("✅ ENTRY-SIGNAL! → BUY LOGIK HIER")

                # Hier kannst du buy_xrp() aus deinem Bot einfügen

        except Exception as e:

            print("❌ Fehler beim Abrufen:", str(e))

        time.sleep(600)  # 10 Minuten warten

def backtest():

    print("📊 Starte Backtest...")

    df = fetch_ohlcv(limit=200)

    df["SMA50"] = df["close"].rolling(SMA_PERIOD).mean()

    signals = []

    for i in range(SMA_PERIOD + 1, len(df)):

        curr = df.iloc[i]

        prev = df.iloc[i - 1]

        if (

            curr["close"] < prev["close"] * DROP_THRESHOLD and

            curr["close"] > df["SMA50"].iloc[i]

        ):

            signals.append(curr["timestamp"])

    print(f"✅ {len(signals)} Entry-Signale gefunden.")

    for t in signals:

        print("📈", t)

# Starte live oder backtest

if __name__ == "__main__":

    # Für Live-Betrieb → live_loop()

    # Für Backtest → backtest()

    backtest()

    # live_loop()
 
