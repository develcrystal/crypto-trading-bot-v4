_value'] = starting_value * df['cumulative_returns'] / df['cumulative_returns'].iloc[0]
            
            # Berechne Drawdown
            df['cumulative_max'] = df['portfolio_value'].cummax()
            df['drawdown'] = (df['portfolio_value'] / df['cumulative_max'] - 1) * 100
            
            print(f"✅ Portfolio-Performance berechnet")
            print(f"Start-Wert: ${starting_value:.2f}")
            print(f"Aktueller Wert: ${df['portfolio_value'].iloc[-1]:.2f}")
            print(f"Max Drawdown: {df['drawdown'].min():.2f}%")
            
            # Berechne Performance-Metriken
            total_return = (df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0] - 1) * 100
            print(f"Gesamtrendite: {total_return:.2f}%")
        else:
            print("❌ Keine Performance Chart Daten")
    except Exception as e:
        print(f"❌ Performance Chart Test Fehler: {str(e)}")
    
    print("\n----- TEST: LIVE SIGNALS PANEL -----")
    try:
        df = client.get_market_data(symbol="BTCUSDT", interval=5, limit=100)
        if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
            print(f"✅ Live Signals Data: {len(df)} 5-Minuten-Kerzen geladen")
            
            # Simuliere Signal-Generierung (vereinfacht)
            df['sma9'] = df['close'].rolling(window=9).mean()
            df['sma20'] = df['close'].rolling(window=20).mean()
            
            # Letzte Kreuzung prüfen
            last_cross_up = (df['sma9'].iloc[-2] <= df['sma20'].iloc[-2]) and (df['sma9'].iloc[-1] > df['sma20'].iloc[-1])
            last_cross_down = (df['sma9'].iloc[-2] >= df['sma20'].iloc[-2]) and (df['sma9'].iloc[-1] < df['sma20'].iloc[-1])
            
            if last_cross_up:
                print("🟢 BUY Signal generiert (SMA9 kreuzt SMA20 nach oben)")
            elif last_cross_down:
                print("🔴 SELL Signal generiert (SMA9 kreuzt SMA20 nach unten)")
            else:
                print("⚪ Kein Signal (SMA9 und SMA20 kreuzen nicht)")
            
            # Volumen-Check (wie im Dashboard)
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            
            if current_volume > avg_volume * 1.5:
                print(f"📊 Hohes Volumen: {current_volume:.2f} (150% über Durchschnitt)")
            else:
                print(f"📊 Normales Volumen: {current_volume:.2f}")
        else:
            print("❌ Keine Live Signals Daten")
    except Exception as e:
        print(f"❌ Live Signals Test Fehler: {str(e)}")
    
    print("\n----- DASHBOARD INTEGRATION GESAMTERGEBNIS -----")
    overall_success = True
    
    try:
        # Test: Market Regime
        df1 = client.get_market_data(symbol="BTCUSDT", interval="240", limit=100)
        test1 = df1 is not None and isinstance(df1, pd.DataFrame) and not df1.empty
        
        # Test: Performance Charts
        df2 = client.get_market_data(symbol="BTCUSDT", interval=1440, limit=30)
        test2 = df2 is not None and isinstance(df2, pd.DataFrame) and not df2.empty
        
        # Test: Live Signals
        df3 = client.get_market_data(symbol="BTCUSDT", interval=5, limit=100)
        test3 = df3 is not None and isinstance(df3, pd.DataFrame) and not df3.empty
        
        overall_success = test1 and test2 and test3
        
        if overall_success:
            print("\n🎉 ERFOLG: Alle Dashboard-Panels können mit dem fixierten Client korrekt funktionieren!")
            print("Das Dashboard sollte nun in der Lage sein, echte Marktdaten zu laden und anzuzeigen.")
        else:
            print("\n⚠️ TEILWEISE ERFOLG: Nicht alle Tests waren erfolgreich.")
            print(f"Market Regime Panel: {'✅' if test1 else '❌'}")
            print(f"Performance Charts Panel: {'✅' if test2 else '❌'}")
            print(f"Live Signals Panel: {'✅' if test3 else '❌'}")
    except Exception as e:
        print(f"\n❌ FEHLER: Gesamttest fehlgeschlagen: {str(e)}")

if __name__ == "__main__":
    test_dashboard_integration()
