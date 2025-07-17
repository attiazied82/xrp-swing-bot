import os

import time

from binance.client import Client

from binance.enums import *

from decimal import Decimal, ROUND_DOWN

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("5huWOQsBrwBCFPTL6YBPxzpV0pCZHx5nd9qDm9MB5CHngY2OCglQmlDlsqBBE0VV")

API_SECRET = os.getenv("0uaiZXnDF5S1k17kz3DPRla4XSisTVYHZ7qvuQ9Bb4WVwsDhNdbv2Pad6xzXAuc0")

client = Client(API_KEY, API_SECRET)

SYMBOL = "XRPEUR"

EUR_PORTION = 0.9   # 90 % des EUR-Guthabens verwenden

MIN_XRP = Decimal('10.0')  # Mindestmenge laut Binance

def get_step_size(symbol):

    info = client.get_symbol_info(symbol)

    for f in info['filters']:

        if f['filterType'] == 'LOT_SIZE':

            return Decimal(f['stepSize'])

    raise Exception("Step size konnte nicht geladen werden")

def get_price(symbol):

    ticker = client.get_symbol_ticker(symbol=symbol)

    return Decimal(ticker['price'])

def get_balance(asset='EUR'):

    balance = client.get_asset_balance(asset=asset)

    return Decimal(balance['free'])

def round_step_size(quantity, step_size):

    return (quantity // step_size) * step_size

def place_order_with_tp_sl(symbol, price, atr):

    eur_balance = get_balance('EUR')

    amount_to_spend = eur_balance * Decimal(str(EUR_PORTION))

    step_size = get_step_size(symbol)

    xrp_price = get_price(symbol)

    # XRP-Menge berechnen

    raw_qty = amount_to_spend / xrp_price

    qty = round_step_size(raw_qty, step_size)

    if qty < MIN_XRP:

        print(f"❌ Kaufmenge ({qty}) unter Mindestgröße ({MIN_XRP}). Kein Kauf.")

        return

    print(f"📈 Marktpreis: {xrp_price:.4f}, EUR: {eur_balance}, XRP Menge: {qty}")

    # SL / TP berechnen

    stop_price = (xrp_price - atr * 2).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)

    tp_price = (xrp_price + atr * 3).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)

    print(f"🛡️ SL bei {stop_price}, 🎯 TP bei {tp_price}")

    try:

        # Markt-Kauf

        buy = client.order_market_buy(

            symbol=symbol,

            quantity=float(qty)

        )

        print("✅ Kauf erfolgreich:", buy)

        # OCO-Order für TP & SL

        oco = client.create_oco_order(

            symbol=symbol,

            side=SIDE_SELL,

            quantity=float(qty),

            price=str(tp_price),                     # Take Profit

            stopPrice=str(stop_price),              # Stop Trigger

            stopLimitPrice=str(stop_price - Decimal('0.0010')),  # Stop-Limit

            stopLimitTimeInForce=TIME_IN_FORCE_GTC

        )

        print("✅ TP/SL OCO-Order gesetzt:", oco)

    except Exception as e:

        print("❌ Binance-Fehler:", e)

# Beispielhafter Durchlauf

if __name__ == "__main__":

    while True:

        try:

            current_price = get_price(SYMBOL)

            atr = Decimal('0.015')  # Beispielwert oder von Strategie ableiten

            print("\n📊 Starte neuen Entry-Versuch...")

            place_order_with_tp_sl(SYMBOL, current_price, atr)

        except Exception as e:

            print("❌ Laufzeitfehler:", e)

        print("⏳ Warte 60 Minuten...")

        time.sleep(3600)
 
