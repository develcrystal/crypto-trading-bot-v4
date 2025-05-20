"""
Risikomanagement-Modul zur Steuerung von Position Sizing, Stop-Loss und Drawdown-Management.
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime


@dataclass
class Position:
    """Datenklasse zur Speicherung von Positionsinformationen."""
    symbol: str
    direction: str  # 'long' oder 'short'
    entry_price: float
    stop_loss: float
    take_profit: Optional[float] = None
    position_size: float = 0.0
    entry_time: Optional[datetime] = None
    risk_amount: float = 0.0
    risk_reward_ratio: float = 0.0
    pip_value: float = 0.0
    trade_id: Optional[str] = None
    notes: Optional[str] = None


class RiskManager:
    """
    Risikomanagement-Klasse für Crypto Trading Bot.
    Verantwortlich für Position Sizing, Stop-Loss-Berechnung und Drawdown-Management.
    """
    
    def __init__(self, account_balance: float, risk_per_trade_pct: float = 2.0, 
                 max_drawdown_pct: float = 10.0, max_risk_per_day_pct: float = 5.0,
                 max_trades_per_day: int = 5, max_position_size_pct: float = 20.0,
                 min_risk_reward_ratio: float = 1.5, max_correlation: float = 0.7,
                 leverage: int = 1):
        """
        Initialisiert den RiskManager.
        
        :param account_balance: Aktuelles Kontoguthaben
        :param risk_per_trade_pct: Maximales Risiko pro Trade in Prozent
        :param max_drawdown_pct: Maximaler erlaubter Drawdown in Prozent
        :param max_risk_per_day_pct: Maximales Risiko pro Tag in Prozent
        :param max_trades_per_day: Maximale Anzahl an Trades pro Tag
        :param max_position_size_pct: Maximale Positionsgröße in Prozent des Guthabens
        :param min_risk_reward_ratio: Minimales Risiko-Ertrags-Verhältnis
        :param max_correlation: Maximale Korrelation zwischen Positionen
        :param leverage: Hebelwirkung
        """
        self.account_balance = account_balance
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_risk_per_day_pct = max_risk_per_day_pct
        self.max_trades_per_day = max_trades_per_day
        self.max_position_size_pct = max_position_size_pct
        self.min_risk_reward_ratio = min_risk_reward_ratio
        self.max_correlation = max_correlation
        self.leverage = leverage
        
        # Tracking-Eigenschaften
        self.current_drawdown_pct = 0.0
        self.peak_balance = account_balance
        self.open_positions: List[Position] = []
        self.closed_positions: List[Dict] = []
        self.daily_trades: Dict[str, int] = {}
        self.daily_risk_used: Dict[str, float] = {}
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                               risk_adjustment: float = 1.0, symbol: str = "BTCUSDT") -> float:
        """
        Berechnet die optimale Positionsgröße basierend auf Risikoprofil.
        
        :param entry_price: Einstandskurs
        :param stop_loss: Stop-Loss-Level
        :param risk_adjustment: Anpassungsfaktor für das Risiko (1.0 = normal, <1.0 = reduziert, >1.0 = erhöht)
        :param symbol: Handelssymbol
        :return: Optimale Positionsgröße
        """
        # Berechne Risiko pro Trade in Währung
        risk_amount = self.account_balance * (self.risk_per_trade_pct / 100) * risk_adjustment
        
        # Berechne Risiko pro Einheit
        risk_per_unit = abs(entry_price - stop_loss)
        
        # Berechne Positionsgröße (unter Berücksichtigung von Hebel)
        position_size = (risk_amount / risk_per_unit) * self.leverage
        
        # Begrenze die Positionsgröße auf einen maximalen Anteil des Guthabens
        max_position = self.account_balance * (self.max_position_size_pct / 100) * self.leverage
        position_size = min(position_size, max_position)
        
        return position_size
    
    def validate_trade(self, entry_price: float, stop_loss: float, take_profit: Optional[float] = None, 
                       symbol: str = "BTCUSDT", direction: str = "long") -> Dict:
        """
        Überprüft, ob ein Trade den Risikomanagement-Kriterien entspricht.
        
        :param entry_price: Einstandskurs
        :param stop_loss: Stop-Loss-Level
        :param take_profit: Take-Profit-Level (optional)
        :param symbol: Handelssymbol
        :param direction: Handelsrichtung ('long' oder 'short')
        :return: Dictionary mit Validierungsergebnissen
        """
        validation_result = {
            "valid": True,
            "reasons": [],
            "position_size": 0.0,
            "risk_amount": 0.0,
            "risk_reward_ratio": 0.0
        }
        
        # Prüfe Richtung
        if direction not in ["long", "short"]:
            validation_result["valid"] = False
            validation_result["reasons"].append(f"Ungültige Richtung: {direction}")
            return validation_result
        
        # Prüfe Stop-Loss-Platzierung
        if (direction == "long" and stop_loss >= entry_price) or \
           (direction == "short" and stop_loss <= entry_price):
            validation_result["valid"] = False
            validation_result["reasons"].append("Stop-Loss ist ungültig platziert")
            return validation_result
        
        # Prüfe Take-Profit, falls angegeben
        if take_profit is not None:
            if (direction == "long" and take_profit <= entry_price) or \
               (direction == "short" and take_profit >= entry_price):
                validation_result["valid"] = False
                validation_result["reasons"].append("Take-Profit ist ungültig platziert")
                return validation_result
            
            # Berechne Risiko-Ertrags-Verhältnis
            risk = abs(entry_price - stop_loss)
            reward = abs(entry_price - take_profit)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            validation_result["risk_reward_ratio"] = risk_reward_ratio
            
            # Prüfe, ob das Risiko-Ertrags-Verhältnis ausreichend ist
            if risk_reward_ratio < self.min_risk_reward_ratio:
                validation_result["valid"] = False
                validation_result["reasons"].append(
                    f"Risiko-Ertrags-Verhältnis {risk_reward_ratio:.2f} ist unter dem Minimum von {self.min_risk_reward_ratio}"
                )
        
        # Prüfe Drawdown
        if self.current_drawdown_pct >= self.max_drawdown_pct:
            validation_result["valid"] = False
            validation_result["reasons"].append(
                f"Maximaler Drawdown erreicht: {self.current_drawdown_pct:.2f}% vs. {self.max_drawdown_pct}%"
            )
        
        # Prüfe tägliches Risiko
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_risk_used = self.daily_risk_used.get(today_str, 0.0)
        risk_amount = self.account_balance * (self.risk_per_trade_pct / 100)
        
        if (daily_risk_used + self.risk_per_trade_pct) > self.max_risk_per_day_pct:
            validation_result["valid"] = False
            validation_result["reasons"].append(
                f"Maximales tägliches Risiko erreicht: {daily_risk_used:.2f}% + {self.risk_per_trade_pct:.2f}% > {self.max_risk_per_day_pct:.2f}%"
            )
        
        # Prüfe maximale Anzahl von Trades pro Tag
        daily_trades = self.daily_trades.get(today_str, 0)
        if daily_trades >= self.max_trades_per_day:
            validation_result["valid"] = False
            validation_result["reasons"].append(
                f"Maximale Anzahl von Trades pro Tag erreicht: {daily_trades} >= {self.max_trades_per_day}"
            )
        
        # Berechne Positionsgröße und Risikobetrag
        if validation_result["valid"]:
            position_size = self.calculate_position_size(entry_price, stop_loss, 1.0, symbol)
            risk_amount = self.account_balance * (self.risk_per_trade_pct / 100)
            
            validation_result["position_size"] = position_size
            validation_result["risk_amount"] = risk_amount
        
        return validation_result
    
    def open_position(self, symbol: str, direction: str, entry_price: float, stop_loss: float, 
                     take_profit: Optional[float] = None, position_size: Optional[float] = None,
                     risk_adjustment: float = 1.0, notes: Optional[str] = None) -> Optional[Position]:
        """
        Öffnet eine neue Position, wenn sie den Risikomanagement-Kriterien entspricht.
        
        :param symbol: Handelssymbol
        :param direction: Handelsrichtung ('long' oder 'short')
        :param entry_price: Einstandskurs
        :param stop_loss: Stop-Loss-Level
        :param take_profit: Take-Profit-Level (optional)
        :param position_size: Positionsgröße (wenn None, wird automatisch berechnet)
        :param risk_adjustment: Anpassungsfaktor für das Risiko
        :param notes: Zusätzliche Notizen zur Position
        :return: Position-Objekt, wenn erfolgreich, sonst None
        """
        # Validiere den Trade
        validation = self.validate_trade(entry_price, stop_loss, take_profit, symbol, direction)
        
        if not validation["valid"]:
            print(f"Trade konnte nicht ausgeführt werden: {', '.join(validation['reasons'])}")
            return None
        
        # Berechne Positionsgröße, falls nicht angegeben
        if position_size is None:
            position_size = self.calculate_position_size(
                entry_price, stop_loss, risk_adjustment, symbol
            )
        
        # Berechne Risikobeträge
        risk_per_unit = abs(entry_price - stop_loss)
        risk_amount = position_size * risk_per_unit / self.leverage
        
        # Berechne Risiko-Ertrags-Verhältnis
        risk_reward_ratio = 0.0
        if take_profit is not None:
            reward = abs(entry_price - take_profit)
            risk_reward_ratio = reward / risk_per_unit if risk_per_unit > 0 else 0
        
        # Erstelle Position
        position = Position(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            entry_time=datetime.now(),
            risk_amount=risk_amount,
            risk_reward_ratio=risk_reward_ratio,
            trade_id=f"{symbol}-{direction}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            notes=notes
        )
        
        # Aktualisiere Tracking-Informationen
        self.open_positions.append(position)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.daily_trades[today_str] = self.daily_trades.get(today_str, 0) + 1
        self.daily_risk_used[today_str] = self.daily_risk_used.get(today_str, 0) + self.risk_per_trade_pct
        
        return position
    
    def close_position(self, position: Position, exit_price: float, exit_time: Optional[datetime] = None,
                      exit_reason: str = "manual") -> Dict:
        """
        Schließt eine offene Position und aktualisiert das Konto.
        
        :param position: Position, die geschlossen werden soll
        :param exit_price: Ausstiegskurs
        :param exit_time: Ausstiegszeit (wenn None, wird die aktuelle Zeit verwendet)
        :param exit_reason: Grund für das Schließen
        :return: Dictionary mit Informationen zum geschlossenen Trade
        """
        if exit_time is None:
            exit_time = datetime.now()
        
        # Berechne P&L
        if position.direction == "long":
            profit_loss = (exit_price - position.entry_price) * position.position_size
        else:
            profit_loss = (position.entry_price - exit_price) * position.position_size
        
        profit_loss_pct = (profit_loss / self.account_balance) * 100
        
        # Aktualisiere Konto
        self.account_balance += profit_loss
        
        # Aktualisiere Drawdown
        if self.account_balance > self.peak_balance:
            self.peak_balance = self.account_balance
        else:
            self.current_drawdown_pct = ((self.peak_balance - self.account_balance) / self.peak_balance) * 100
        
        # Erstelle Informationen zum geschlossenen Trade
        closed_trade = {
            "symbol": position.symbol,
            "direction": position.direction,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "entry_time": position.entry_time,
            "exit_time": exit_time,
            "position_size": position.position_size,
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "risk_amount": position.risk_amount,
            "risk_reward_ratio": position.risk_reward_ratio,
            "trade_id": position.trade_id,
            "exit_reason": exit_reason,
            "notes": position.notes
        }
        
        # Entferne die Position aus den offenen Positionen
        self.open_positions = [p for p in self.open_positions if p.trade_id != position.trade_id]
        
        # Füge sie zu den geschlossenen Positionen hinzu
        self.closed_positions.append(closed_trade)
        
        return closed_trade
    
    def adjust_stop_loss(self, position: Position, new_stop_loss: float) -> bool:
        """
        Passt den Stop-Loss einer bestehenden Position an.
        
        :param position: Position, deren Stop-Loss angepasst werden soll
        :param new_stop_loss: Neuer Stop-Loss-Level
        :return: True, wenn erfolgreich, sonst False
        """
        # Validiere den neuen Stop-Loss
        if position.direction == "long" and new_stop_loss > position.stop_loss:
            position.stop_loss = new_stop_loss
            return True
        elif position.direction == "short" and new_stop_loss < position.stop_loss:
            position.stop_loss = new_stop_loss
            return True
        
        return False
    
    def calculate_portfolio_risk(self) -> Dict:
        """
        Berechnet das Gesamtrisiko des aktuellen Portfolios.
        
        :return: Dictionary mit Risikoinformationen
        """
        if not self.open_positions:
            return {
                "total_risk_amount": 0.0,
                "total_risk_pct": 0.0,
                "max_drawdown_pct": self.current_drawdown_pct,
                "position_count": 0
            }
        
        total_risk_amount = sum(position.risk_amount for position in self.open_positions)
        total_risk_pct = (total_risk_amount / self.account_balance) * 100
        
        return {
            "total_risk_amount": total_risk_amount,
            "total_risk_pct": total_risk_pct,
            "max_drawdown_pct": self.current_drawdown_pct,
            "position_count": len(self.open_positions)
        }
    
    def reset_daily_limits(self) -> None:
        """
        Setzt die täglichen Limits zurück.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.daily_trades[today_str] = 0
        self.daily_risk_used[today_str] = 0.0
    
    def update_account_balance(self, new_balance: float) -> None:
        """
        Aktualisiert den Kontostand und berechnet den Drawdown neu.
        
        :param new_balance: Neuer Kontostand
        """
        self.account_balance = new_balance
        
        # Aktualisiere Peak-Balance und Drawdown
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
            self.current_drawdown_pct = 0.0
        else:
            self.current_drawdown_pct = ((self.peak_balance - new_balance) / self.peak_balance) * 100
    
    def get_performance_metrics(self) -> Dict:
        """
        Gibt Leistungsmetriken für das Risikomanagement zurück.
        
        :return: Dictionary mit Leistungsmetriken
        """
        if not self.closed_positions:
            return {
                "win_rate": 0.0,
                "avg_profit_pct": 0.0,
                "avg_loss_pct": 0.0,
                "profit_factor": 0.0,
                "expectancy": 0.0,
                "max_drawdown": self.current_drawdown_pct,
                "sharpe_ratio": 0.0,
                "total_trades": 0
            }
        
        # Berechne Win-Rate
        profitable_trades = [t for t in self.closed_positions if t["profit_loss"] > 0]
        win_rate = len(profitable_trades) / len(self.closed_positions)
        
        # Berechne durchschnittlichen Gewinn und Verlust
        profits = [t["profit_loss_pct"] for t in self.closed_positions if t["profit_loss"] > 0]
        losses = [t["profit_loss_pct"] for t in self.closed_positions if t["profit_loss"] <= 0]
        
        avg_profit_pct = np.mean(profits) if profits else 0.0
        avg_loss_pct = np.mean(losses) if losses else 0.0
        
        # Berechne Profit-Faktor
        total_profit = sum(profits)
        total_loss = abs(sum(losses))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Berechne Expectancy
        expectancy = (win_rate * avg_profit_pct) - ((1 - win_rate) * abs(avg_loss_pct))
        
        # Berechne Sharpe Ratio (vereinfacht)
        returns = [t["profit_loss_pct"] for t in self.closed_positions]
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe_ratio = mean_return / std_return if std_return > 0 else 0.0
        
        return {
            "win_rate": win_rate,
            "avg_profit_pct": avg_profit_pct,
            "avg_loss_pct": avg_loss_pct,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "max_drawdown": self.current_drawdown_pct,
            "sharpe_ratio": sharpe_ratio,
            "total_trades": len(self.closed_positions)
        }
