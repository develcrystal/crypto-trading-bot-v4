#!/usr/bin/env python
"""
Multi-Regime Backtest Script für umfassende Marktphasen-Analyse.

Dieses Script testet die Smart Money Strategie über verschiedene 
Marktphasen (Bull, Bear, Sideways) und vergleicht die Performance.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

# Hinzufügen des Projektverzeichnisses zum Python-Pfad
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Lokale Module
from data.data_handler import DataHandler
from backtesting.backtest_engine import BacktestEngine
from exchange.bybit_api import BybitAPI
from config.config import config
from strategies.smart_money import SmartMoneyStrategy
from strategies.enhanced_smart_money import EnhancedSmartMoneyStrategy

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketRegimeAnalyzer:
    """
    Analyzer für Performance über verschiedene Marktphasen.
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialisiert den Market Regime Analyzer.
        
        Args:
            initial_balance: Anfangsguthaben für Backtests
        """
        self.initial_balance = initial_balance
        self.results = {}
        
        # Test-Perioden für verschiedene Marktphasen
        self.test_periods = [
            {
                'name': 'Q1_2024_Bull',
                'start_date': '2024-01-01',
                'end_date': '2024-03-31',
                'expected_regime': 'bull',
                'description': 'Q1 2024 Bull Run (BTC: ~40k -> ~65k)'
            },
            {
                'name': 'Q2_2024_Mixed', 
                'start_date': '2024-04-01',
                'end_date': '2024-06-30',
                'expected_regime': 'sideways',
                'description': 'Q2 2024 Volatil/Sideways (BTC: 60k-70k)'
            },
            {
                'name': 'Q3_2024_Bear',
                'start_date': '2024-07-01', 
                'end_date': '2024-09-30',
                'expected_regime': 'bear',
                'description': 'Q3 2024 Summer Correction (BTC: 70k -> 50k)'
            },
            {
                'name': 'Q4_2024_Recovery',
                'start_date': '2024-10-01',
                'end_date': '2024-12-31', 
                'expected_regime': 'bull',
                'description': 'Q4 2024 Election Recovery (BTC: 50k -> 90k+)'
            },
            {
                'name': 'Recent_3M',
                'start_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
                'expected_regime': 'mixed',
                'description': 'Recent 3 Months'
            }
        ]
        
        # Exchange API initialisieren
        self.exchange_api = BybitAPI(testnet=True)
        self.data_handler = DataHandler(self.exchange_api)
    
    def run_regime_comparison(self, symbol: str = 'BTCUSDT', timeframe: str = '1h') -> Dict:
        """
        Führt Backtests über alle Marktphasen durch und vergleicht die Ergebnisse.
        
        Args:
            symbol: Trading-Symbol
            timeframe: Zeitrahmen
            
        Returns:
            Dictionary mit Vergleichsergebnissen
        """
        logger.info(f"🚀 Starte Multi-Regime Backtest Analyse für {symbol}")
        logger.info(f"📊 Analysiere {len(self.test_periods)} verschiedene Marktphasen")
        
        comparison_results = {
            'symbol': symbol,
            'timeframe': timeframe,
            'test_periods': self.test_periods,
            'classic_strategy_results': {},
            'enhanced_strategy_results': {},
            'regime_analysis': {},
            'performance_comparison': {}
        }
        
        # Konfigurationen vorbereiten
        classic_config = self._prepare_classic_config()
        enhanced_config = self._prepare_enhanced_config()
        
        for period in self.test_periods:
            logger.info(f"\n📅 Teste Periode: {period['name']} ({period['start_date']} - {period['end_date']})")
            logger.info(f"📈 Erwarteter Markttyp: {period['expected_regime']}")
            logger.info(f"📝 Beschreibung: {period['description']}")
            
            try:
                # Test mit Classic Smart Money Strategy
                logger.info("🔧 Teste Classic Smart Money Strategy...")
                classic_results = self._run_single_backtest(
                    strategy_class=SmartMoneyStrategy,
                    config=classic_config,
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=period['start_date'],
                    end_date=period['end_date'],
                    period_name=f"{period['name']}_classic"
                )
                
                if classic_results:
                    comparison_results['classic_strategy_results'][period['name']] = classic_results
                    logger.info(f"✅ Classic Strategy: {classic_results['metrics']['return']:.2%} Return, "
                              f"{classic_results['metrics']['total_trades']} Trades")
                
                # Test mit Enhanced Strategy (mit Market Regime Detection)
                logger.info("🔧 Teste Enhanced Smart Money Strategy...")
                enhanced_results = self._run_single_backtest(
                    strategy_class=EnhancedSmartMoneyStrategy,
                    config=enhanced_config,
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=period['start_date'],
                    end_date=period['end_date'],
                    period_name=f"{period['name']}_enhanced"
                )
                
                if enhanced_results:
                    comparison_results['enhanced_strategy_results'][period['name']] = enhanced_results
                    logger.info(f"✅ Enhanced Strategy: {enhanced_results['metrics']['return']:.2%} Return, "
                              f"{enhanced_results['metrics']['total_trades']} Trades")
                    
                    # Extrahiere Regime-Informationen
                    if 'regime_detection' in enhanced_results:
                        comparison_results['regime_analysis'][period['name']] = enhanced_results['regime_detection']
                
            except Exception as e:
                logger.error(f"❌ Fehler bei Periode {period['name']}: {e}")
                continue
        
        # Performance-Vergleich durchführen
        comparison_results['performance_comparison'] = self._analyze_performance_comparison(
            comparison_results['classic_strategy_results'],
            comparison_results['enhanced_strategy_results']
        )
        
        # Gesamtbericht erstellen
        self._generate_regime_report(comparison_results)
        
        return comparison_results
    
    def _prepare_classic_config(self) -> Dict:
        """Bereitet Konfiguration für Classic Strategy vor."""
        classic_config = vars(config).copy()
        return classic_config
    
    def _prepare_enhanced_config(self) -> Dict:
        """Bereitet Konfiguration für Enhanced Strategy vor."""
        enhanced_config = vars(config).copy()
        
        # Enhanced Strategy spezifische Parameter
        enhanced_config.update({
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
        })
        
        return enhanced_config
    
    def _run_single_backtest(self, strategy_class, config: Dict, symbol: str, 
                           timeframe: str, start_date: str, end_date: str,
                           period_name: str) -> Dict:
        """
        Führt einen einzelnen Backtest durch.
        
        Args:
            strategy_class: Strategie-Klasse
            config: Konfiguration
            symbol: Trading-Symbol
            timeframe: Zeitrahmen
            start_date: Startdatum
            end_date: Enddatum
            period_name: Name der Periode
            
        Returns:
            Backtest-Ergebnisse
        """
        try:
            # Strategie-Instanz erstellen
            strategy = strategy_class(config)
            
            # Backtest-Engine initialisieren
            backtest_engine = BacktestEngine(
                data_handler=self.data_handler,
                strategy=strategy,
                initial_balance=self.initial_balance,
                commission=0.001,
                slippage=0.0005
            )
            
            # Backtest durchführen
            results = backtest_engine.run(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            if results.get('success'):
                # Zusätzliche Analyse für Enhanced Strategy
                if hasattr(strategy, 'get_regime_summary'):
                    results['regime_detection'] = strategy.get_regime_summary()
                
                # Speichere Ergebnisse
                output_dir = 'backtest_results_regime_analysis'
                os.makedirs(output_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = f"{output_dir}/{period_name}_{timestamp}.json"
                backtest_engine.save_results(results_file)
                
                logger.info(f"💾 Ergebnisse gespeichert: {results_file}")
                
                return results
            else:
                logger.error(f"❌ Backtest fehlgeschlagen: {results.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Backtest: {e}")
            return None
    
    def _analyze_performance_comparison(self, classic_results: Dict, enhanced_results: Dict) -> Dict:
        """
        Analysiert und vergleicht die Performance zwischen Classic und Enhanced Strategy.
        
        Args:
            classic_results: Ergebnisse der Classic Strategy
            enhanced_results: Ergebnisse der Enhanced Strategy
            
        Returns:
            Performance-Vergleichsanalyse
        """
        comparison = {
            'classic_performance': {},
            'enhanced_performance': {},
            'improvement_analysis': {},
            'regime_effectiveness': {}
        }
        
        # Gesamtperformance aggregieren
        for strategy_name, results_dict in [('classic', classic_results), ('enhanced', enhanced_results)]:
            total_return = 0
            total_trades = 0
            total_wins = 0
            total_profit = 0
            max_drawdown = 0
            
            period_performances = []
            
            for period_name, period_results in results_dict.items():
                if period_results and 'metrics' in period_results:
                    metrics = period_results['metrics']
                    
                    period_performances.append({
                        'period': period_name,
                        'return': metrics.get('return', 0),
                        'trades': metrics.get('total_trades', 0),
                        'win_rate': metrics.get('win_rate', 0),
                        'profit_factor': metrics.get('profit_factor', 0),
                        'max_drawdown': metrics.get('max_drawdown', 0),
                        'sharpe_ratio': metrics.get('sharpe_ratio', 0)
                    })
                    
                    total_return += metrics.get('return', 0)
                    total_trades += metrics.get('total_trades', 0)
                    total_wins += metrics.get('total_trades', 0) * metrics.get('win_rate', 0)
                    total_profit += metrics.get('net_profit', 0)
                    max_drawdown = max(max_drawdown, metrics.get('max_drawdown', 0))
            
            # Durchschnitt über alle Perioden
            num_periods = len(period_performances)
            avg_return = total_return / num_periods if num_periods > 0 else 0
            avg_win_rate = total_wins / total_trades if total_trades > 0 else 0
            
            performance_key = f'{strategy_name}_performance'
            comparison[performance_key] = {
                'period_details': period_performances,
                'aggregate_metrics': {
                    'average_return': avg_return,
                    'total_trades': total_trades,
                    'average_win_rate': avg_win_rate,
                    'total_profit': total_profit,
                    'max_drawdown': max_drawdown,
                    'consistency': np.std([p['return'] for p in period_performances]) if period_performances else 0
                }
            }
        
        # Verbesserungsanalyse
        if comparison['classic_performance']['aggregate_metrics'] and comparison['enhanced_performance']['aggregate_metrics']:
            classic_agg = comparison['classic_performance']['aggregate_metrics']
            enhanced_agg = comparison['enhanced_performance']['aggregate_metrics']
            
            comparison['improvement_analysis'] = {
                'return_improvement': enhanced_agg['average_return'] - classic_agg['average_return'],
                'win_rate_improvement': enhanced_agg['average_win_rate'] - classic_agg['average_win_rate'],
                'profit_improvement': enhanced_agg['total_profit'] - classic_agg['total_profit'],
                'drawdown_improvement': classic_agg['max_drawdown'] - enhanced_agg['max_drawdown'],
                'consistency_improvement': classic_agg['consistency'] - enhanced_agg['consistency'],
                'relative_return_improvement': (enhanced_agg['average_return'] / classic_agg['average_return'] - 1) * 100 if classic_agg['average_return'] != 0 else 0
            }
        
        return comparison
    
    def _generate_regime_report(self, results: Dict) -> None:
        """
        Generiert einen umfassenden Bericht über die Marktphasen-Analyse.
        
        Args:
            results: Vergleichsergebnisse
        """
        print("\n" + "="*80)
        print("🏆 CRYPTO TRADING BOT V2 - MARKTPHASEN-ANALYSE BERICHT")
        print("="*80)
        print(f"🎯 Symbol: {results['symbol']}")
        print(f"⏰ Timeframe: {results['timeframe']}")
        print(f"📅 Analysierte Perioden: {len(results['test_periods'])}")
        print(f"💰 Anfangsguthaben: ${self.initial_balance:,.2f}")
        
        # Performance-Vergleich
        if 'performance_comparison' in results:
            comp = results['performance_comparison']
            
            print("\n📊 PERFORMANCE-VERGLEICH")
            print("-" * 50)
            
            # Classic Strategy
            if 'classic_performance' in comp:
                classic = comp['classic_performance']['aggregate_metrics']
                print(f"🔵 Classic Smart Money Strategy:")
                print(f"   Durchschnittlicher Return: {classic['average_return']:.2%}")
                print(f"   Gesamte Trades: {classic['total_trades']}")
                print(f"   Durchschnittliche Win Rate: {classic['average_win_rate']:.2%}")
                print(f"   Max Drawdown: {classic['max_drawdown']:.2%}")
                print(f"   Return-Konsistenz (Std): {classic['consistency']:.2%}")
            
            # Enhanced Strategy
            if 'enhanced_performance' in comp:
                enhanced = comp['enhanced_performance']['aggregate_metrics']
                print(f"\n🟢 Enhanced Smart Money Strategy (mit Market Regime Detection):")
                print(f"   Durchschnittlicher Return: {enhanced['average_return']:.2%}")
                print(f"   Gesamte Trades: {enhanced['total_trades']}")
                print(f"   Durchschnittliche Win Rate: {enhanced['average_win_rate']:.2%}")
                print(f"   Max Drawdown: {enhanced['max_drawdown']:.2%}")
                print(f"   Return-Konsistenz (Std): {enhanced['consistency']:.2%}")
            
            # Verbesserungsanalyse
            if 'improvement_analysis' in comp:
                improvements = comp['improvement_analysis']
                print(f"\n⚡ VERBESSERUNGS-ANALYSE:")
                print(f"   Return-Verbesserung: {improvements['return_improvement']:+.2%}")
                print(f"   Relative Return-Verbesserung: {improvements['relative_return_improvement']:+.1f}%")
                print(f"   Win Rate-Verbesserung: {improvements['win_rate_improvement']:+.2%}")
                print(f"   Drawdown-Verbesserung: {improvements['drawdown_improvement']:+.2%}")
                print(f"   Konsistenz-Verbesserung: {improvements['consistency_improvement']:+.2%}")
        
        # Periode-spezifische Ergebnisse
        print("\n📈 PERFORMANCE NACH MARKTPHASEN")
        print("-" * 50)
        
        for period in results['test_periods']:
            period_name = period['name']
            print(f"\n🗓️  {period['description']} ({period_name})")
            
            # Classic Results
            if period_name in results.get('classic_strategy_results', {}):
                classic = results['classic_strategy_results'][period_name]['metrics']
                print(f"    🔵 Classic: {classic['return']:+.2%} return, {classic['total_trades']} trades, {classic['win_rate']:.1%} win rate")
            
            # Enhanced Results  
            if period_name in results.get('enhanced_strategy_results', {}):
                enhanced = results['enhanced_strategy_results'][period_name]['metrics']
                print(f"    🟢 Enhanced: {enhanced['return']:+.2%} return, {enhanced['total_trades']} trades, {enhanced['win_rate']:.1%} win rate")
                
                # Regime Detection Info
                if period_name in results.get('regime_analysis', {}):
                    regime_info = results['regime_analysis'][period_name]
                    print(f"    🧠 Erkanntes Regime: {regime_info.get('current_regime', 'unknown')} (Confidence: {regime_info.get('confidence', 0):.2f})")
        
        # Schlussfolgerungen
        print("\n🎯 SCHLUSSFOLGERUNGEN")
        print("-" * 50)
        
        if 'improvement_analysis' in results.get('performance_comparison', {}):
            improvements = results['performance_comparison']['improvement_analysis']
            
            if improvements['relative_return_improvement'] > 5:
                print("✅ Enhanced Strategy mit Market Regime Detection zeigt signifikante Verbesserungen!")
                print(f"   → {improvements['relative_return_improvement']:.1f}% bessere Returns")
            elif improvements['relative_return_improvement'] > 0:
                print("📈 Enhanced Strategy zeigt leichte Verbesserungen")
                print(f"   → {improvements['relative_return_improvement']:.1f}% bessere Returns")
            else:
                print("📊 Beide Strategien zeigen ähnliche Performance")
                print("   → Market Regime Detection hat in diesem Zeitraum keinen signifikanten Vorteil gezeigt")
            
            if improvements['consistency_improvement'] > 0:
                print("🎯 Enhanced Strategy ist konsistenter über verschiedene Marktphasen")
            
            if improvements['drawdown_improvement'] > 0:
                print(f"🛡️  Enhanced Strategy reduziert Drawdown um {improvements['drawdown_improvement']:.2%}")
        
        print("\n💡 EMPFEHLUNGEN")
        print("-" * 50)
        print("1. ✅ Verwende Enhanced Strategy für Live-Trading")
        print("2. 🔄 Kontinuierliche Überwachung der Regime-Detection-Genauigkeit")
        print("3. 📊 Backteste neue Marktperioden regelmäßig")
        print("4. ⚙️  Feintuning der Regime-spezifischen Parameter")
        
        print("\n" + "="*80)
        
        # Speichere detaillierten Report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"backtest_results_regime_analysis/market_regime_analysis_report_{timestamp}.txt"
        
        os.makedirs('backtest_results_regime_analysis', exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(f"Market Regime Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(f"Results: {results}\n")
        
        logger.info(f"📄 Detaillierter Report gespeichert: {report_file}")

def main():
    """Hauptfunktion für Multi-Regime Backtest."""
    print("🚀 Starte Multi-Regime Backtest für Crypto Trading Bot V2")
    
    # Analyzer initialisieren
    analyzer = MarketRegimeAnalyzer(initial_balance=10000.0)
    
    # Umfassende Regime-Analyse durchführen
    try:
        results = analyzer.run_regime_comparison(
            symbol='BTCUSDT',
            timeframe='1h'
        )
        
        print("\n✅ Multi-Regime Backtest erfolgreich abgeschlossen!")
        print("📊 Detaillierte Ergebnisse siehe Konsolen-Output und gespeicherte Dateien")
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Multi-Regime Backtest: {e}")

if __name__ == "__main__":
    main()
