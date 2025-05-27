"""
Enhanced Smart Money Strategy mit Market Regime Detection für verschiedene Marktphasen.

Diese erweiterte Version der Smart Money Strategie erkennt automatisch Marktphasen
(Bull, Bear, Sideways) und passt die Trading-Parameter entsprechend an.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union
from strategies.smart_money import SmartMoneyStrategy

logger = logging.getLogger(__name__)

class EnhancedSmartMoneyStrategy(SmartMoneyStrategy):
    """
    Erweiterte Smart Money Strategie mit Market Regime Detection.
    
    Zusätzliche Features:
    - Automatische Erkennung von Bull/Bear/Sideways Markets
    - Anpassung der Filter-Sensitivität basierend auf Marktphase
    - Dynamische Volumen-Schwellen je nach Marktregime
    - Verbesserte Risk-Reward-Ratios für verschiedene Phasen
    """
    
    def __init__(self, config: Dict):
        """
        Initialisiert die Enhanced Smart Money Strategy.
        
        Args:
            config: Konfigurationsparameter
        """
        super().__init__(config)
        self.name = "EnhancedSmartMoneyStrategy"
        
        # Explizit die Attribute aus der Basisklasse übernehmen
        self.liquidity_factor = config.get('LIQUIDITY_FACTOR', 1.0)
        self.min_liquidity_threshold = config.get('MIN_LIQUIDITY_THRESHOLD', 1000)
        
        # Market Regime Detection Parameter
        self.trend_lookback = config.get('TREND_LOOKBACK', 50)  # Perioden für Trendanalyse
        self.volatility_lookback = config.get('VOLATILITY_LOOKBACK', 20)  # Für Volatilitätsanalyse
        self.sideways_threshold = config.get('SIDEWAYS_THRESHOLD', 0.02)  # 2% für Sideways-Erkennung
        
        # Marktspezifische Multiplikatoren
        self.market_multipliers = config.get('MARKET_MULTIPLIERS', {
            'bull': {
                'volume_threshold_multiplier': 0.8,  # Weniger restriktiv bei Volumens
                'risk_reward_multiplier': 1.2,       # Höhere Targets in Bull-Markets
                'liquidity_factor_multiplier': 1.1   # Mehr Liquiditäts-Fokus
            },
            'bear': {
                'volume_threshold_multiplier': 1.2,  # Restriktiver bei Volumen
                'risk_reward_multiplier': 0.9,       # Konservativer in Bear-Markets
                'liquidity_factor_multiplier': 1.3   # Viel Fokus auf Liquidität
            },
            'sideways': {
                'volume_threshold_multiplier': 1.5,  # Sehr selektiv
                'risk_reward_multiplier': 1.0,       # Standard Targets
                'liquidity_factor_multiplier': 1.0   # Standard Liquidität
            }
        })
        
        # Aktueller Marktzustand
        self.current_market_regime = None
        self.regime_confidence = 0.0
        
        logger.info(f"EnhancedSmartMoneyStrategy initialisiert mit Market Regime Detection")
    
    def detect_market_regime(self, data: pd.DataFrame) -> Tuple[str, float]:
        """
        Erkennt den aktuellen Marktzustand (Bull, Bear, Sideways).
        
        Args:
            data: DataFrame mit Marktdaten
            
        Returns:
            Tuple mit (market_regime, confidence)
        """
        if len(data) < self.trend_lookback:
            return 'unknown', 0.0
        
        # Benutze die letzten N Perioden für Analyse
        recent_data = data.tail(self.trend_lookback)
        current_price = recent_data['close'].iloc[-1]
        start_price = recent_data['close'].iloc[0]
        
        # Trendrichtung berechnen
        total_return = (current_price - start_price) / start_price
        
        # Volatilität berechnen
        returns = recent_data['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Moving Averages für Trend-Bestätigung
        if len(recent_data) >= 20:
            sma_20 = recent_data['close'].rolling(20).mean().iloc[-1]
            sma_50 = recent_data['close'].rolling(min(50, len(recent_data))).mean().iloc[-1]
        else:
            sma_20 = current_price
            sma_50 = current_price
        
        # Zusätzliche Trend-Indikatoren
        price_above_ma20 = current_price > sma_20
        price_above_ma50 = current_price > sma_50
        ma20_above_ma50 = sma_20 > sma_50
        
        # Volume Trend (wenn verfügbar)
        volume_trend = 0
        if 'volume' in recent_data.columns:
            recent_volume = recent_data['volume'].tail(10).mean()
            earlier_volume = recent_data['volume'].head(10).mean()
            volume_trend = (recent_volume - earlier_volume) / earlier_volume if earlier_volume > 0 else 0
        
        # Regime-Bestimmung
        confidence = 0.0
        
        # Bull Market Indikatoren
        bull_score = 0
        if total_return > 0.05:  # 5%+ Anstieg
            bull_score += 3
        elif total_return > 0.02:  # 2%+ Anstieg
            bull_score += 2
        elif total_return > 0:
            bull_score += 1
            
        if price_above_ma20 and price_above_ma50:
            bull_score += 2
        elif price_above_ma20 or price_above_ma50:
            bull_score += 1
            
        if ma20_above_ma50:
            bull_score += 1
            
        if volume_trend > 0.1:  # Steigendes Volumen
            bull_score += 1
            
        # Bear Market Indikatoren
        bear_score = 0
        if total_return < -0.05:  # 5%+ Rückgang
            bear_score += 3
        elif total_return < -0.02:  # 2%+ Rückgang
            bear_score += 2
        elif total_return < 0:
            bear_score += 1
            
        if not price_above_ma20 and not price_above_ma50:
            bear_score += 2
        elif not price_above_ma20 or not price_above_ma50:
            bear_score += 1
            
        if not ma20_above_ma50:
            bear_score += 1
            
        if volume_trend > 0.1:  # Hohe Volatilität in Bear Markets
            bear_score += 1
        
        # Sideways Market Detection
        sideways_score = 0
        if abs(total_return) < self.sideways_threshold:
            sideways_score += 3
            
        if volatility < returns.quantile(0.3):  # Niedrige Volatilität
            sideways_score += 2
            
        # Entscheidung treffen
        max_score = max(bull_score, bear_score, sideways_score)
        
        if max_score >= 4:
            confidence = min(max_score / 8.0, 1.0)  # Max Confidence 1.0
            
            if bull_score == max_score:
                regime = 'bull'
            elif bear_score == max_score:
                regime = 'bear'
            else:
                regime = 'sideways'
        else:
            # Niedrige Confidence, verwende Fallback
            if total_return > 0.01:
                regime = 'bull'
                confidence = 0.3
            elif total_return < -0.01:
                regime = 'bear'
                confidence = 0.3
            else:
                regime = 'sideways'
                confidence = 0.5
        
        return regime, confidence
    
    def adjust_parameters_for_regime(self, regime: str, confidence: float) -> Dict:
        """
        Passt Strategie-Parameter basierend auf Marktregime an.
        
        Args:
            regime: Erkannter Marktzustand
            confidence: Confidence-Level der Erkennung
            
        Returns:
            Dictionary mit angepassten Parametern
        """
        if regime not in self.market_multipliers:
            regime = 'sideways'  # Fallback
        
        multipliers = self.market_multipliers[regime]
        
        # Parameter anpassen
        adjusted_params = {
            'adjusted_volume_threshold': int(self.volume_threshold * multipliers['volume_threshold_multiplier']),
            'adjusted_risk_reward_ratio': self.risk_reward_ratio * multipliers['risk_reward_multiplier'],
            'adjusted_liquidity_factor': self.liquidity_factor * multipliers['liquidity_factor_multiplier'],
            'market_regime': regime,
            'regime_confidence': confidence
        }
        
        # Confidence-basierte Anpassungen
        if confidence < 0.5:
            # Bei niedriger Confidence: konservativer
            adjusted_params['adjusted_volume_threshold'] = int(adjusted_params['adjusted_volume_threshold'] * 1.2)
            adjusted_params['adjusted_risk_reward_ratio'] = min(adjusted_params['adjusted_risk_reward_ratio'], self.risk_reward_ratio)
        
        return adjusted_params
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Erweiterte Indikator-Berechnung mit Market Regime Detection.
        
        Args:
            data: DataFrame mit Marktdaten
            
        Returns:
            DataFrame mit Indikatoren und Marktregime-Informationen
        """
        # Basis-Indikatoren berechnen
        df = super().calculate_indicators(data)
        
        if len(df) < self.trend_lookback:
            # Nicht genug Daten für Regime-Detection
            df['market_regime'] = 'unknown'
            df['regime_confidence'] = 0.0
            df['adjusted_volume_threshold'] = self.volume_threshold
            df['adjusted_risk_reward_ratio'] = self.risk_reward_ratio
            df['adjusted_liquidity_factor'] = self.liquidity_factor
            return df
        
        # Market Regime Detection
        regime, confidence = self.detect_market_regime(df)
        self.current_market_regime = regime
        self.regime_confidence = confidence
        
        # Parameter anpassen
        adjusted_params = self.adjust_parameters_for_regime(regime, confidence)
        
        # Informationen zum DataFrame hinzufügen
        df['market_regime'] = regime
        df['regime_confidence'] = confidence
        df['adjusted_volume_threshold'] = adjusted_params['adjusted_volume_threshold']
        df['adjusted_risk_reward_ratio'] = adjusted_params['adjusted_risk_reward_ratio']
        df['adjusted_liquidity_factor'] = adjusted_params['adjusted_liquidity_factor']
        
        # Trend-Stärke Indikator
        if len(df) >= 20:
            df['trend_strength'] = abs(df['close'].pct_change(20).fillna(0))
        else:
            df['trend_strength'] = 0
        
        logger.debug(f"Market Regime: {regime} (Confidence: {confidence:.2f})")
        
        return df
    
    def generate_signal(self, data: pd.DataFrame, current_position: str = None) -> Tuple[str, float, float, Dict]:
        """
        Generiert erweiterte Handelssignale mit Marktregime-Anpassung.
        
        Args:
            data: DataFrame mit Marktdaten und Indikatoren
            current_position: Aktuelle Position
            
        Returns:
            Tuple mit (signal, entry_price, stop_loss, metadata)
        """
        # Basis-Signal generieren
        signal, entry_price, stop_loss, metadata = super().generate_signal(data, current_position)
        
        if data.empty:
            return signal, entry_price, stop_loss, metadata
        
        latest_candle = data.iloc[-1]
        
        # Marktregime-Informationen hinzufügen
        market_regime = latest_candle.get('market_regime', 'unknown')
        regime_confidence = latest_candle.get('regime_confidence', 0.0)
        adjusted_volume_threshold = latest_candle.get('adjusted_volume_threshold', self.volume_threshold)
        
        # Signal-Modifikation basierend auf Marktregime
        if signal in ['BUY', 'SELL']:
            # Volumen-Check mit angepasster Schwelle
            if latest_candle['volume'] < adjusted_volume_threshold:
                signal = 'HOLD'
                metadata['regime_filter'] = f"Volume {latest_candle['volume']:.0f} < regime-adjusted threshold {adjusted_volume_threshold:.0f}"
                logger.info(f"Signal gefiltert durch Marktregime ({market_regime}): Volumen zu niedrig")
            else:
                # Signal bestätigt - erweitere Metadaten
                metadata['market_regime'] = market_regime
                metadata['regime_confidence'] = regime_confidence
                metadata['adjusted_volume_threshold'] = adjusted_volume_threshold
                
                # Angepasste Stop-Loss Berechnung
                if not np.isnan(stop_loss) and market_regime == 'bear':
                    # In Bear Markets: engere Stop-Losses
                    if signal == 'BUY':
                        stop_loss = stop_loss * 1.05  # 5% enger
                    elif signal == 'SELL':
                        stop_loss = stop_loss * 0.95  # 5% enger
                elif not np.isnan(stop_loss) and market_regime == 'bull':
                    # In Bull Markets: weitere Stop-Losses für mehr Spielraum
                    if signal == 'BUY':
                        stop_loss = stop_loss * 0.95  # 5% weiter
                    elif signal == 'SELL':
                        stop_loss = stop_loss * 1.05  # 5% weiter
                
                logger.info(f"Signal {signal} bestätigt in {market_regime} market (confidence: {regime_confidence:.2f})")
        
        # Zusätzliche Regime-basierte Filter
        if signal in ['BUY', 'SELL'] and regime_confidence < 0.3:
            # Bei sehr niedriger Confidence: nur sehr starke Signale erlauben
            if not all([
                metadata.get('buy_filters_passed', {}).get('volume', False),
                metadata.get('buy_filters_passed', {}).get('key_levels', False),
                metadata.get('buy_filters_passed', {}).get('pattern', False)
            ]) and signal == 'BUY':
                signal = 'HOLD'
                metadata['low_confidence_filter'] = True
            elif not all([
                metadata.get('sell_filters_passed', {}).get('volume', False),
                metadata.get('sell_filters_passed', {}).get('key_levels', False),
                metadata.get('sell_filters_passed', {}).get('pattern', False)
            ]) and signal == 'SELL':
                signal = 'HOLD'
                metadata['low_confidence_filter'] = True
        
        return signal, entry_price, stop_loss, metadata
    
    def get_regime_summary(self) -> Dict:
        """
        Gibt eine Zusammenfassung des aktuellen Marktregimes zurück.
        
        Returns:
            Dictionary mit Regime-Informationen
        """
        return {
            'current_regime': self.current_market_regime,
            'confidence': self.regime_confidence,
            'trend_lookback': self.trend_lookback,
            'sideways_threshold': self.sideways_threshold,
            'market_multipliers': self.market_multipliers
        }

# Beispiel für die Verwendung
if __name__ == "__main__":
    # Test-Konfiguration mit Market Regime Settings
    test_config = {
        'LIQUIDITY_FACTOR': 1.0,
        'MIN_LIQUIDITY_THRESHOLD': 1000,
        'SESSION_MULTIPLIER': {'asian': 0.8, 'london': 1.2, 'new_york': 1.5},
        'RSI_PERIOD': 14,
        'MACD_FAST': 9,
        'MACD_SLOW': 21,
        'ATR_PERIOD': 14,
        'VOLATILITY_THRESHOLD': 0.03,
        'SR_LOOKBACK': 14,
        'RISK_REWARD_RATIO': 1.5,
        'POSITION_SIZE': 0.01,
        'RISK_PERCENTAGE': 2.0,
        'USE_VOLUME_FILTER': True,
        'VOLUME_THRESHOLD': 100000,
        'USE_KEY_LEVELS': True,
        'USE_PATTERN_RECOGNITION': True,
        'USE_ORDER_FLOW': False,
        'USE_LIQUIDITY_SWEEP': False,
        
        # Enhanced Settings
        'TREND_LOOKBACK': 50,
        'VOLATILITY_LOOKBACK': 20,
        'SIDEWAYS_THRESHOLD': 0.02,
        'MARKET_MULTIPLIERS': {
            'bull': {
                'volume_threshold_multiplier': 0.8,
                'risk_reward_multiplier': 1.2,
                'liquidity_factor_multiplier': 1.1
            },
            'bear': {
                'volume_threshold_multiplier': 1.2,
                'risk_reward_multiplier': 0.9,
                'liquidity_factor_multiplier': 1.3
            },
            'sideways': {
                'volume_threshold_multiplier': 1.5,
                'risk_reward_multiplier': 1.0,
                'liquidity_factor_multiplier': 1.0
            }
        }
    }
    
    # Strategie-Instanz erstellen
    strategy = EnhancedSmartMoneyStrategy(test_config)
    
    # Test mit synthetischen Daten
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='1H'),
        'open': np.random.rand(100) * 1000 + 40000,
        'high': np.random.rand(100) * 1000 + 40500,
        'low': np.random.rand(100) * 1000 + 39500,
        'close': np.random.rand(100) * 1000 + 40000,
        'volume': np.random.rand(100) * 50000 + 50000
    })
    data = data.set_index('timestamp')
    
    # Simuliere einen Trend
    trend = np.linspace(0, 0.1, 100)  # 10% Anstieg
    data['close'] = data['close'] * (1 + trend)
    data['high'] = data['high'] * (1 + trend)
    data['low'] = data['low'] * (1 + trend)
    data['open'] = data['open'] * (1 + trend)
    
    # Teste Enhanced Strategy
    data_with_indicators = strategy.calculate_indicators(data)
    signal, entry_price, stop_loss, metadata = strategy.generate_signal(data_with_indicators)
    
    print(f"Enhanced Smart Money Strategy Test:")
    print(f"Market Regime: {strategy.current_market_regime} (Confidence: {strategy.regime_confidence:.2f})")
    print(f"Generated Signal: {signal}")
    print(f"Entry Price: {entry_price}")
    print(f"Stop Loss: {stop_loss}")
    print(f"Metadata: {metadata}")
    
    # Regime Summary
    regime_summary = strategy.get_regime_summary()
    print(f"\nRegime Summary: {regime_summary}")
