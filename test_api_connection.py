#!/usr/bin/env python3
"""
Test-Skript für die Verbindung zu Bybit Mainnet mit den konfigurierten API-Credentials.
"""

import os
import sys
import logging
from datetime import datetime

# Füge das Projekt-Verzeichnis zum Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des API-Clients
from core.api_client import BybitAPIClient

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("api_test")

def test_api_connection():
    """
    Testet die Verbindung zu Bybit mit den konfigurierten API-Credentials.
    """
    try:
        # API-Client erstellen
        logger.info("Initialisiere Bybit API Client...")
        api = BybitAPIClient()
        
        # Testnet-Status ausgeben
        logger.info(f"Testnet Mode: {api.testnet}")
        logger.info(f"API Base URL: {api.base_url}")
        
        # Prüfe API-Authentifizierung durch Wallet-Abfrage
        logger.info("Teste Wallet-Balance-Abfrage (benötigt Authentifizierung)...")
        balance = api.get_wallet_balance()
        
        if balance['success']:
            logger.info(f"API-Authentifizierung erfolgreich!")
            logger.info(f"Account-Typ: {balance['account_type']}")
            logger.info(f"USDT-Wert: ${balance['total_usdt_value']:.2f}")
            logger.info("Balances:")
            for coin, amount in balance['balances'].items():
                logger.info(f"   {coin}: {amount}")
        else:
            logger.error(f"API-Authentifizierungsfehler: {balance.get('error', 'Unbekannt')}")
            return False
        
        # Prüfe Marktdaten-Abruf
        logger.info("Teste Marktdaten-Abruf...")
        ticker = api.get_ticker("BTCUSDT")
        
        if ticker['success']:
            logger.info(f"Marktdaten-Abruf erfolgreich!")
            logger.info(f"BTC-Preis: ${ticker['price']:,.2f}")
            logger.info(f"24h Change: {ticker['change_24h']:+.2f}%")
        else:
            logger.error(f"Marktdaten-Abruf fehlgeschlagen: {ticker.get('error', 'Unbekannt')}")
            return False
        
        # Prüfe Orderbuch-Abruf
        logger.info("Teste Orderbuch-Abruf...")
        orderbook = api.get_order_book("BTCUSDT", 5)
        
        if orderbook['success']:
            logger.info(f"Orderbuch-Abruf erfolgreich!")
            top_bid = orderbook['bids'][0] if orderbook['bids'] else None
            top_ask = orderbook['asks'][0] if orderbook['asks'] else None
            
            if top_bid:
                logger.info(f"Top Bid: ${top_bid[0]:,.2f} ({top_bid[1]:,.6f} BTC)")
            if top_ask:
                logger.info(f"Top Ask: ${top_ask[0]:,.2f} ({top_ask[1]:,.6f} BTC)")
        else:
            logger.error(f"Orderbuch-Abruf fehlgeschlagen: {orderbook.get('error', 'Unbekannt')}")
            return False
        
        # Prüfe Dashboard-Daten
        logger.info("Teste Dashboard-Daten-Abruf...")
        dashboard = api.get_dashboard_data()
        
        if dashboard['success']:
            logger.info(f"Dashboard-Daten-Abruf erfolgreich!")
            logger.info(f"Portfolio-Wert: ${dashboard['portfolio_value']:,.2f}")
            logger.info(f"BTC-Preis: ${dashboard['btc_price']:,.2f}")
        else:
            logger.error(f"Dashboard-Daten-Abruf fehlgeschlagen: {dashboard.get('error', 'Unbekannt')}")
            return False
        
        # Prüfe offene Orders
        logger.info("Teste Abfrage offener Orders...")
        open_orders = api.get_open_orders()
        
        if open_orders['success']:
            logger.info(f"Abfrage offener Orders erfolgreich!")
            order_count = len(open_orders.get('orders', []))
            logger.info(f"Anzahl offener Orders: {order_count}")
        else:
            logger.error(f"Abfrage offener Orders fehlgeschlagen: {open_orders.get('error', 'Unbekannt')}")
            return False
        
        logger.info("=" * 50)
        logger.info("ALLE API-TESTS ERFOLGREICH!")
        logger.info("=" * 50)
        logger.info(f"API-Verbindung zu Bybit {'TESTNET' if api.testnet else 'MAINNET'} ist voll funktionsfähig!")
        logger.info(f"Account ist für Live Trading bereit!")
        logger.info(f"Portfolio-Wert: ${dashboard['portfolio_value']:,.2f}")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim API-Test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("BYBIT API CONNECTION TEST - MAINNET LIVE CHECK")
    print("=" * 80)
    
    success = test_api_connection()
    
    if success:
        print("\nMAINNET READY FOR LIVE TRADING!")
        print("Du kannst jetzt das Live Dashboard starten mit:")
        print("\npython ui/main_dashboard.py")
    else:
        print("\nAPI CONNECTION TEST FAILED")
        print("Bitte überprüfe deine API-Credentials in der .env-Datei.")
