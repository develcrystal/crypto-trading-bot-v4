import os
from pybit.unified_trading import HTTP
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

# Bybit API-Schlüssel aus Umgebungsvariablen
api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")
testnet = os.getenv("TESTNET", "true").lower() == "true"

if not api_key or not api_secret:
    print("Fehler: BYBIT_API_KEY oder BYBIT_API_SECRET nicht in der .env-Datei gefunden.")
    exit()

# Initialisiere die Bybit HTTP-Sitzung
session = HTTP(
    testnet=testnet,
    api_key=api_key,
    api_secret=api_secret
)

print(f"Verbinde mit Bybit {'Testnet' if testnet else 'Mainnet'}...")

try:
    # Beispiel: Eine Market Buy Order für BTCUSDT platzieren
    # Bitte passe SYMBOL, QTY und CATEGORY nach Bedarf an
    symbol = "BTCUSDT"
    qty = "0.001"  # Kleinste Menge für BTCUSDT


    print(f"Platziere Market Buy Order für {qty} {symbol} auf {category}...")
    order_response = session.place_order(
        category=category,
        symbol=symbol,
        side="Buy",
        orderType="Market",
        qty=qty,
        # Für Market Orders ist der Preis nicht erforderlich
        # timeInForce="GTC" # Good Till Cancel
    )

    print("\nOrder-Antwort:")
    print(order_response)

    if order_response and order_response.get("retCode") == 0:
        print(f"\n✅ Order erfolgreich platziert! Order ID: {order_response['result']['orderId']}")
    else:
        print(f"\n❌ Fehler beim Platzieren der Order: {order_response.get('retMsg', 'Unbekannter Fehler')}")

except Exception as e:
    print(f"\nEin Fehler ist aufgetreten: {e}")