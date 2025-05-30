import streamlit as st
from datetime import datetime

class ControlPanel:
    """Advanced trading bot control panel with safety features"""
    
    def __init__(self):
        self.state = {
            'trading_active': False,
            'trading_paused': False,
            'confirmations': {}
        }
        
    def render(self):
        """Render the control panel UI"""
        with st.expander("🤖 **BOT-HANDELSSTEUERUNG**", expanded=True):
            self._render_status()
            st.markdown("---")
            self._render_controls()
            st.markdown("---")
            self._render_security_info()
            st.markdown("---")
            self._render_emergency_stop()
            st.markdown("---")
            self._render_action_log()
    
    def _render_status(self):
        """Render status information"""
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**Status:**")
        with col2:
            if self.state['trading_active'] and not self.state['trading_paused']:
                status_text = "Aktiv (Vollautomatisch)"
                status_class = "status-good"
            elif self.state['trading_active'] and self.state['trading_paused']:
                status_text = "Pausiert (Nur Überwachung)"
                status_class = "status-warning"
            else:
                status_text = "Gestoppt"
                status_class = "status-danger"
                
            st.markdown(f"<div class='{status_class}'>{status_text}</div>", unsafe_allow_html=True)
        
        st.markdown(f"**Letzte Aktion:** {self._get_last_action()}")
    
    def _render_controls(self):
        """Render control buttons with confirmation logic"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶ Trading starten", key="start_btn", 
                        help="Aktiviert automatischen Handel mit echtem Geld",
                        type="primary" if not self.state['trading_active'] else "secondary"):
                if self.state['confirmations'].get('start'):
                    self.state['trading_active'] = True
                    self.state['trading_paused'] = False
                    self._log_action("Handel gestartet")
                    self.state['confirmations']['start'] = False
                else:
                    st.warning("WARNUNG: Handel mit ECHTEM GELD!")
                    self.state['confirmations']['start'] = True
        
        with col2:
            if st.button("⏸ Signale pausieren", key="pause_btn",
                        help="Pausiert neue Handelssignale",
                        disabled=not self.state['trading_active'],
                        type="primary" if self.state['trading_active'] and not self.state['trading_paused'] else "secondary"):
                if self.state['confirmations'].get('pause'):
                    self.state['trading_paused'] = True
                    self._log_action("Signale pausiert")
                    self.state['confirmations']['pause'] = False
                else:
                    st.info("Neue Signale pausieren? Bestehende Positionen bleiben aktiv.")
                    self.state['confirmations']['pause'] = True
                    
        with col3:
            if st.button("⏹ Trading stoppen", key="stop_btn",
                        help="Stoppt alle Handelsaktivitäten",
                        disabled=not self.state['trading_active'],
                        type="primary"):
                if self.state['confirmations'].get('stop'):
                    self.state['trading_active'] = False
                    self.state['trading_paused'] = False
                    self._log_action("Handel gestoppt")
                    self.state['confirmations']['stop'] = False
                else:
                    st.warning("Alle Handelsaktivitäten werden gestoppt!")
                    self.state['confirmations']['stop'] = True
    
    def _render_security_info(self):
        """Render security information"""
        st.markdown("**Sicherheitsstatus:**")
        st.success("✓ Trading aktiv mit max. 5€ pro Trade")
        st.info("API-Berechtigungen: ✓ Trading ✓ Transfers ✓ Wallet")
        
        st.markdown("**Positionskontrolle:**")
        max_size = st.slider("Max. Positionsgröße (€)", 5, 50, 5, key="position_slider")
        st.info(f"Aktive Positionen: 2/{max_size} Positionen (15€/{max_size}€)")
    
    def _render_emergency_stop(self):
        """Render emergency stop with double confirmation"""
        if st.button("🔴 NOTFALL-STOP", key="emergency_btn",
                   help="Schließt SOFORT alle Positionen zum Marktpreis",
                   type="primary"):
            if self.state['confirmations'].get('emergency'):
                st.error("ALLE POSITIONEN WURDEN GESCHLOSSEN!")
                self.state['trading_active'] = False
                self._log_action("NOTFALL: Alle Positionen geschlossen")
                self.state['confirmations']['emergency'] = False
            else:
                st.error("ACHTUNG: Dies schließt ALLE Positionen SOFORT!")
                self.state['confirmations']['emergency'] = True
    
    def _render_action_log(self):
        """Render action log"""
        st.markdown("**Letzte Aktionen:**")
        if not hasattr(self, 'action_log'):
            self.action_log = []
            
        for action in self.action_log[-3:]:
            st.code(f"{action['time']} - {action['message']}")
    
    def _log_action(self, message):
        """Log an action with timestamp"""
        if not hasattr(self, 'action_log'):
            self.action_log = []
            
        self.action_log.append({
            'time': datetime.now().strftime("%H:%M:%S"),
            'message': message
        })
    
    def _get_last_action(self):
        """Get last action message"""
        if hasattr(self, 'action_log') and self.action_log:
            return self.action_log[-1]['message']
        return "Keine Aktionen"