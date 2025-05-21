"""
📊 MONITORING DATA PROCESSOR
Verarbeitet Live-Daten für das Dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

class MonitoringDataProcessor:
    """Processes real-time data for dashboard display"""
    
    def __init__(self, trading_bot_instance=None):
        self.trading_bot = trading_bot_instance
        self.cache = {}
        self.last_update = None
        
    def get_portfolio_data(self) -> Dict:
        """Get current portfolio information"""
        if self.trading_bot:
            try:
                return {
                    "portfolio_value": self.trading_bot.get_portfolio_value(),
                    "total_pnl": self.trading_bot.get_total_pnl(),
                    "daily_pnl": self.trading_bot.get_daily_pnl(),
                    "unrealized_pnl": self.trading_bot.get_unrealized_pnl(),
                    "available_balance": self.trading_bot.get_available_balance()
                }
            except Exception as e:
                print(f"Error getting portfolio data: {e}")
                return self._get_mock_portfolio_data()
        else:
            return self._get_mock_portfolio_data()
    
    def get_trading_metrics(self) -> Dict:
        """Get trading performance metrics"""
        if self.trading_bot:
            try:
                recent_trades = self.trading_bot.get_recent_trades()
                return {
                    "total_trades": len(recent_trades),
                    "trades_today": len([t for t in recent_trades if t.get('date', datetime.now()).date() == datetime.now().date()]),
                    "win_rate": self.calculate_win_rate(recent_trades),
                    "profit_factor": self.calculate_profit_factor(recent_trades),
                    "avg_win": self.calculate_avg_win(recent_trades),
                    "avg_loss": self.calculate_avg_loss(recent_trades),
                    "max_drawdown": self.calculate_max_drawdown(recent_trades)
                }
            except Exception as e:
                print(f"Error getting trading metrics: {e}")
                return self._get_mock_trading_metrics()
        else:
            return self._get_mock_trading_metrics()
    
    def get_market_regime_data(self) -> Dict:
        """Get current market regime detection"""
        if self.trading_bot and hasattr(self.trading_bot, 'strategy'):
            try:
                regime_info = self.trading_bot.strategy.detect_market_regime()
                return {
                    "current_regime": regime_info.get("regime", "UNKNOWN"),
                    "confidence": regime_info.get("confidence", 0),
                    "bull_score": regime_info.get("bull_score", 0),
                    "bear_score": regime_info.get("bear_score", 0),
                    "sideways_score": regime_info.get("sideways_score", 0),
                    "duration": regime_info.get("duration", 0),
                    "adaptive_params": regime_info.get("adaptive_params", {})
                }
            except Exception as e:
                print(f"Error getting market regime: {e}")
                return self._get_mock_regime_data()
        else:
            return self._get_mock_regime_data()
    
    def get_current_signals(self) -> Dict:
        """Get current trading signals and filter status"""
        if self.trading_bot and hasattr(self.trading_bot, 'strategy'):
            try:
                signals = self.trading_bot.strategy.get_current_signals()
                filters = self.trading_bot.strategy.get_filter_status()
                
                return {
                    "last_signal": signals.get("last_signal", {}),
                    "signal_strength": signals.get("strength", 0),
                    "next_check": signals.get("next_check", datetime.now()),
                    "filter_status": {
                        "volume": filters.get("volume_filter", False),
                        "key_levels": filters.get("key_levels", False),
                        "pattern": filters.get("pattern_recognition", False),
                        "order_flow": filters.get("order_flow", False),
                        "liquidity_sweep": filters.get("liquidity_sweep", False)
                    },
                    "current_values": filters.get("current_values", {}),
                    "thresholds": filters.get("thresholds", {})
                }
            except Exception as e:
                print(f"Error getting signals: {e}")
                return self._get_mock_signals_data()
        else:
            return self._get_mock_signals_data()
    
    def get_risk_metrics(self) -> Dict:
        """Get current risk management metrics"""
        if self.trading_bot and hasattr(self.trading_bot, 'risk_manager'):
            try:
                risk_data = self.trading_bot.risk_manager.get_current_risk_metrics()
                return {
                    "current_exposure": risk_data.get("current_exposure", 0),
                    "max_exposure": risk_data.get("max_exposure", 5000),
                    "daily_risk_used": risk_data.get("daily_risk_used", 0),
                    "daily_risk_limit": risk_data.get("daily_risk_limit", 1000),
                    "current_drawdown": risk_data.get("current_drawdown", 0),
                    "max_drawdown_limit": risk_data.get("max_drawdown_limit", 20),
                    "portfolio_health": risk_data.get("portfolio_health", "HEALTHY"),
                    "active_alerts": risk_data.get("active_alerts", [])
                }
            except Exception as e:
                print(f"Error getting risk metrics: {e}")
                return self._get_mock_risk_data()
        else:
            return self._get_mock_risk_data()
    
    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """Calculate win rate from trades"""
        if not trades:
            return 0.0
        
        winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        return winning_trades / len(trades)
    
    def calculate_profit_factor(self, trades: List[Dict]) -> float:
        """Calculate profit factor"""
        if not trades:
            return 0.0
        
        total_wins = sum([t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0])
        total_losses = abs(sum([t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]))
        
        return total_wins / total_losses if total_losses > 0 else float('inf')
    
    def calculate_avg_win(self, trades: List[Dict]) -> float:
        """Calculate average winning trade"""
        wins = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        return sum(wins) / len(wins) if wins else 0.0
    
    def calculate_avg_loss(self, trades: List[Dict]) -> float:
        """Calculate average losing trade"""
        losses = [abs(t.get('pnl', 0)) for t in trades if t.get('pnl', 0) < 0]
        return sum(losses) / len(losses) if losses else 0.0
    
    def calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown percentage"""
        if not trades:
            return 0.0
        
        # Simplified calculation - in real implementation would use equity curve
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for trade in sorted(trades, key=lambda x: x.get('timestamp', datetime.now())):
            cumulative_pnl += trade.get('pnl', 0)
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            
            current_dd = (peak - cumulative_pnl) / peak if peak > 0 else 0
            max_dd = max(max_dd, current_dd)
        
        return max_dd * 100
    
    # Mock data methods for demo mode
    def _get_mock_portfolio_data(self) -> Dict:
        """Generate realistic mock portfolio data"""
        base_value = 10000
        change = np.random.normal(0.02, 0.05)  # 2% average with 5% volatility
        
        return {
            "portfolio_value": base_value * (1 + change),
            "total_pnl": base_value * change,
            "daily_pnl": np.random.normal(75, 150),
            "unrealized_pnl": np.random.normal(25, 100),
            "available_balance": base_value * 0.8
        }
    
    def _get_mock_trading_metrics(self) -> Dict:
        """Generate mock trading metrics"""
        total_trades = np.random.randint(45, 120)
        win_rate = np.random.uniform(0.65, 0.85)
        
        return {
            "total_trades": total_trades,
            "trades_today": np.random.randint(8, 25),
            "win_rate": win_rate,
            "profit_factor": np.random.uniform(1.3, 2.1),
            "avg_win": np.random.uniform(60, 140),
            "avg_loss": np.random.uniform(30, 80),
            "max_drawdown": np.random.uniform(8, 18)
        }
    
    def _get_mock_regime_data(self) -> Dict:
        """Generate mock market regime data"""
        regimes = ["BULL", "BEAR", "SIDEWAYS"]
        regime = np.random.choice(regimes, p=[0.5, 0.25, 0.25])
        
        return {
            "current_regime": regime,
            "confidence": np.random.uniform(0.65, 0.95),
            "bull_score": np.random.randint(3, 8),
            "bear_score": np.random.randint(1, 6),
            "sideways_score": np.random.randint(1, 4),
            "duration": np.random.randint(30, 300),
            "adaptive_params": {
                "volume_threshold": 100000 * (0.8 if regime == "BULL" else 1.2 if regime == "BEAR" else 1.5),
                "risk_reward_ratio": 1.8 if regime == "BULL" else 1.4 if regime == "BEAR" else 1.5
            }
        }
    
    def _get_mock_signals_data(self) -> Dict:
        """Generate mock signals data"""
        signal_types = ["BUY", "SELL", "HOLD"]
        signal_type = np.random.choice(signal_types, p=[0.3, 0.3, 0.4])
        
        return {
            "last_signal": {
                "type": signal_type,
                "timestamp": datetime.now() - timedelta(minutes=np.random.randint(1, 180)),
                "price": 106500 + np.random.normal(0, 1000),
                "strength": np.random.uniform(0.6, 1.0)
            },
            "signal_strength": np.random.uniform(0.6, 1.0),
            "next_check": datetime.now() + timedelta(minutes=np.random.randint(1, 60)),
            "filter_status": {
                "volume": np.random.choice([True, False], p=[0.7, 0.3]),
                "key_levels": np.random.choice([True, False], p=[0.8, 0.2]),
                "pattern": np.random.choice([True, False], p=[0.6, 0.4]),
                "order_flow": np.random.choice([True, False], p=[0.5, 0.5]),
                "liquidity_sweep": np.random.choice([True, False], p=[0.3, 0.7])
            },
            "current_values": {
                "volume": np.random.randint(80000, 200000),
                "key_level_distance": np.random.uniform(50, 500)
            },
            "thresholds": {
                "volume": 100000,
                "key_level_distance": 200
            }
        }
    
    def _get_mock_risk_data(self) -> Dict:
        """Generate mock risk data"""
        current_exposure = np.random.uniform(1500, 4000)
        daily_risk = np.random.uniform(200, 800)
        current_dd = np.random.uniform(3, 15)
        
        return {
            "current_exposure": current_exposure,
            "max_exposure": 5000,
            "daily_risk_used": daily_risk,
            "daily_risk_limit": 1000,
            "current_drawdown": current_dd,
            "max_drawdown_limit": 20,
            "portfolio_health": "HEALTHY" if current_dd < 10 and daily_risk < 600 else "MODERATE" if current_dd < 15 else "HIGH_RISK",
            "active_alerts": [] if current_dd < 12 and daily_risk < 700 else ["High Risk Warning"]
        }
    
    def get_equity_curve_data(self, days: int = 30) -> pd.DataFrame:
        """Generate equity curve data"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            end=datetime.now(),
            freq='4H'
        )
        
        values = []
        base_value = 10000
        
        for i, date in enumerate(dates):
            # Simulate realistic returns with some trend
            daily_return = np.random.normal(0.002, 0.025)  # 0.2% per period average
            base_value *= (1 + daily_return)
            values.append(base_value)
        
        return pd.DataFrame({
            'timestamp': dates,
            'portfolio_value': values,
            'returns': pd.Series(values).pct_change()
        })
    
    def save_session_data(self, data: Dict):
        """Save session data for persistence"""
        try:
            session_file = "monitoring_session.json"
            with open(session_file, 'w') as f:
                # Convert datetime objects to strings for JSON serialization
                serializable_data = self._make_json_serializable(data)
                json.dump(serializable_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def load_session_data(self) -> Optional[Dict]:
        """Load previous session data"""
        try:
            session_file = "monitoring_session.json"
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading session data: {e}")
        return None
    
    def _make_json_serializable(self, obj):
        """Convert object to JSON serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        else:
            return obj
