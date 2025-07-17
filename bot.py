import os
from binance.client import Client
from dotenv import load_dotenv
from decimal import Decimal, ROUND_DOWN
load_dotenv()
API_KEY = os.getenv("5huWOQsBrwBCFPTL6YBPxzpV0pCZHx5nd9qDm9MB5CHngY2OCglQmlDlsqBBE0VV")
API_SECRET = os.getenv("0uaiZXnDF5S1k17kz3DPRla4XSisTVYHZ7qvuQ9Bb4WVwsDhNdbv2Pad6xzXAuc0")
client = Client(API_KEY, API_SECRET)
SYMBOL = "XRPEUR"
EUR_PORTION = Decimal("0.9")
MIN_EUR = Decimal("10.0")
def place_market_buy():
   eur_balance = Decimal(client.get_asset_balance(asset='EUR')['free'])
   print(f"💶 EUR-Guthaben: {eur_balance:.2f}")
   amount_to_spend = eur_balance * EUR_PORTION
   # Binance verlangt mindestens ~10 EUR pro Market-Order
   if amount_to_spend < MIN_EUR:
       print(f"❌ Zu wenig EUR ({amount_to_spend:.2f}) für Kauf. Mindestwert: 10.00")
       return
   try:
       print(f"🛒 Kaufe XRP für {amount_to_spend:.2f} EUR (quoteOrderQty)")
       order = client.order_market_buy(
           symbol=SYMBOL,
           quoteOrderQty=str(amount_to_spend)
       )
       print("✅ Kauf erfolgreich:", order)
   except Exception as e:
       print("❌ Fehler bei Kauf:", e)
if __name__ == "__main__":
   place_market_buy()
