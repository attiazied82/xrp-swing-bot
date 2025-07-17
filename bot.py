from binance.client import Client

client = Client("API_KEY", "API_SECRET")

client.get_symbol_info("XRPEUR")
 
from binance.client import Client

from decimal import Decimal

from dotenv import load_dotenv

import os

load_dotenv()

client = Client(os.getenv("API_KEY"), os.getenv("API_SECRET"))

symbol = "XRPEUR"

eur_balance = Decimal(client.get_asset_balance(asset='EUR')['free'])

print(f"💶 EUR Balance: {eur_balance:.2f}")

amount_to_spend = eur_balance * Decimal("0.9")

print(f"🛒 Versuche Kauf für {amount_to_spend:.2f} EUR mit quoteOrderQty...")

try:

    order = client.order_market_buy(

        symbol=symbol,

        quoteOrderQty=str(amount_to_spend)

    )

    print("✅ Kauf erfolgreich:", order)

except Exception as e:

    print("❌ Fehler:", e)
 
