import os
from binance.client import Client
from binance.enums import *
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
client = Client(API_KEY, API_SECRET)
SYMBOL = "XRPUSDC"
QUOTE_ASSET = "USDC"
SPEND_RATIO = Decimal("0.9")  # 90 % verwenden
MIN_USDC = Decimal("10.0")    # Mindestbetrag für Kauf
def get_balance(asset):
   b = client.get_asset_balance(asset=asset)
   return Decimal(b['free']) if b else Decimal("0")
def get_price():
   return Decimal(client.get_symbol_ticker(symbol=SYMBOL)['price'])
def buy_xrp():
   usdc = get_balance(QUOTE_ASSET)
   print(f"💰 USDC verfügbar: {usdc:.2f}")
   if usdc < MIN_USDC:
       print("❌ Nicht genug USDC für Kauf.")
       return
   amount_to_spend = usdc * SPEND_RATIO
   print(f"🛒 Kaufe XRP für {amount_to_spend:.2f} USDC")
   try:
       order = client.order_market_buy(
           symbol=SYMBOL,
           quoteOrderQty=str(amount_to_spend)  # wie viel USDC investieren
       )
       print("✅ Kauf erfolgreich:", order)
       # Menge aus Order-Response extrahieren
       filled_qty = sum(Decimal(fill['qty']) for fill in order['fills'])
       print(f"📦 Gekauft: {filled_qty} XRP")
       # SL/TP setzen
       price = get_price()
       atr = Decimal("0.015")  # Beispiel-ATR
       sl = round(price - atr * 2, 4)
       tp = round(price + atr * 3, 4)
       print(f"🎯 SL: {sl}, TP: {tp}")
       oco = client.create_oco_order(
           symbol=SYMBOL,
           side=SIDE_SELL,
           quantity=str(round(filled_qty, 1)),  # auf 0.1 XRP runden
           price=str(tp),
           stopPrice=str(sl),
           stopLimitPrice=str(sl - Decimal("0.001")),
           stopLimitTimeInForce=TIME_IN_FORCE_GTC
       )
       print("📌 TP/SL gesetzt:", oco)
   except Exception as e:
       print("❌ Fehler:", e)
if __name__ == "__main__":
   buy_xrp()
