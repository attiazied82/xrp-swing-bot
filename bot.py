import os

from binance.client import Client

from binance.enums import *

from decimal import Decimal, ROUND_DOWN

from dotenv import load_dotenv

# 🔐 .env laden

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_SECRET = os.getenv("API_SECRET")

# Binance Client

client = Client(API_KEY, API_SECRET)

# Parameter

SYMBOL = "XRPUSDC"

QUOTE_ASSET = "USDC"

SPEND_RATIO = Decimal("0.9")   # 90% vom Guthaben verwenden

MIN_USDC = Decimal("10.0")     # Mindestmenge laut Binance

# 🔎 Balance abrufen

def get_balance(asset):

    b = client.get_asset_balance(asset=asset)

    return Decimal(b['free']) if b else Decimal("0")

# 📈 Aktuellen Preis holen

def get_price():

    return Decimal(client.get_symbol_ticker(symbol=SYMBOL)['price'])

# Schrittgröße holen

def get_step_size(symbol):

    info = client.get_symbol_info(symbol)

    for f in info['filters']:

        if f['filterType'] == 'LOT_SIZE':

            return Decimal(f['stepSize'])

    raise Exception("Schrittgröße nicht gefunden")

# Menge sauber runden

def round_to_step(qty, step):

    return (qty // step) * step

# ✅ Hauptfunktion

def buy_xrp():

    usdc = get_balance(QUOTE_ASSET)

    print(f"💰 USDC verfügbar: {usdc:.2f}")

    if usdc < MIN_USDC:

        print("❌ Nicht genug USDC für Kauf.")

        return

    amount_to_spend = usdc * SPEND_RATIO

    print(f"🛒 Kaufe XRP für {amount_to_spend:.2f} USDC")

    try:

        # Markt-Kauf

        order = client.order_market_buy(

            symbol=SYMBOL,

            quoteOrderQty=str(amount_to_spend)

        )

        print("✅ Kauf erfolgreich.")

        # Gekaufte Menge berechnen

        total_qty = sum(Decimal(fill['qty']) for fill in order['fills'])

        step = get_step_size(SYMBOL)

        qty = round_to_step(total_qty, step)

        if qty < Decimal("10"):

            print(f"⚠️ Gekaufte Menge zu klein für Verkauf ({qty}).")

            return

        # SL/TP setzen (z. B. ATR basiert)

        price = get_price()

        atr = Decimal("0.015")  # einfacher ATR-Wert

        sl = (price - atr * 2).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

        tp = (price + atr * 3).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

        print(f"🎯 SL: {sl}, TP: {tp}, Verkauf: {qty}")

        # OCO Order platzieren

        oco = client.create_oco_order(

            symbol=SYMBOL,

            side=SIDE_SELL,

            quantity=str(qty),

            price=str(tp),

            stopPrice=str(sl),

            stopLimitPrice=str(sl - Decimal("0.0010")),

            stopLimitTimeInForce=TIME_IN_FORCE_GTC

        )

        print("📌 TP/SL gesetzt.")

    except Exception as e:

        print("❌ Fehler:", e)

# Startpunkt

if __name__ == "__main__":

    buy_xrp()
 
