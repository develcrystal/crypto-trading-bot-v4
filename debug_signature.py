#!/usr/bin/env python
"""
BYBIT SIGNATURE DEBUG TOOL
Überprüft exakt, wie die Signature generiert wird vs. was Bybit erwartet
"""

import os
import hmac
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

def debug_signature():
    """Debuggt die Signature-Generierung Schritt für Schritt"""
    
    # API Credentials
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    recv_window = '5000'
    
    print("BYBIT SIGNATURE DEBUG")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret[:8]}...")
    print(f"Recv Window: {recv_window}")
    
    # Simuliere exakt das, was bei Account Balance passiert
    timestamp = 1748083670346  # Der exakte Timestamp aus der Fehlermeldung
    query_string = "accountType=UNIFIED"  # Der Query String
    
    print("\nREQUEST DETAILS:")
    print(f"Timestamp: {timestamp}")
    print(f"Query String: {query_string}")
    
    # String für Signature (wie Bybit ihn erwartet)
    expected_string = f"{timestamp}{api_key}{recv_window}{query_string}"
    print(f"\nBYBIT EXPECTS: '{expected_string}'")
    print(f"LENGTH: {len(expected_string)}")
    
    # Signature generieren
    signature = hmac.new(
        api_secret.encode('utf-8'),
        expected_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"\nGENERATED SIGNATURE: {signature}")
    
    # Verschiedene Variationen testen
    print("\nTESTING VARIATIONS:")
    
    # Variation 1: Ohne recv_window
    test1 = f"{timestamp}{api_key}{query_string}"
    sig1 = hmac.new(api_secret.encode('utf-8'), test1.encode('utf-8'), hashlib.sha256).hexdigest()
    print(f"1. Without recv_window: '{test1}' -> {sig1}")
    
    # Variation 2: Mit anderem recv_window Format
    test2 = f"{timestamp}{api_key}5000{query_string}"
    sig2 = hmac.new(api_secret.encode('utf-8'), test2.encode('utf-8'), hashlib.sha256).hexdigest()
    print(f"2. recv_window as int: '{test2}' -> {sig2}")
    
    # Variation 3: Query String Formatierung
    test3 = f"{timestamp}{api_key}{recv_window}accountType%3DUNIFIED"
    sig3 = hmac.new(api_secret.encode('utf-8'), test3.encode('utf-8'), hashlib.sha256).hexdigest()
    print(f"3. URL encoded query: '{test3}' -> {sig3}")
    
    # Test mit aktuellem Timestamp
    print("\nCURRENT TIMESTAMP TEST:")
    current_timestamp = int(time.time() * 1000)
    current_string = f"{current_timestamp}{api_key}{recv_window}{query_string}"
    current_sig = hmac.new(api_secret.encode('utf-8'), current_string.encode('utf-8'), hashlib.sha256).hexdigest()
    print(f"Current time: {current_timestamp}")
    print(f"String: '{current_string}'")
    print(f"Signature: {current_sig}")
    
    # Test verschiedene API Secrets (falls falsch in .env)
    print("\nAPI SECRET VERIFICATION:")
    print(f"Current secret: {api_secret}")
    print(f"Length: {len(api_secret)} characters")
    
    # Teste mit alternativen Secrets (falls Typo)
    alternative_secrets = [
        "6h6PCY2SKTDoXJvMtkJuycPT7XZWOi4N",
        "6h6PCY2SmBTzU73Uh1",  # Der aus dem alten Code
    ]
    
    for i, alt_secret in enumerate(alternative_secrets, 1):
        alt_sig = hmac.new(alt_secret.encode('utf-8'), expected_string.encode('utf-8'), hashlib.sha256).hexdigest()
        print(f"Alt Secret {i}: {alt_secret[:8]}... -> {alt_sig}")

if __name__ == "__main__":
    debug_signature()
