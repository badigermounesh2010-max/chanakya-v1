import logging
from typing import Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DashboardData:
    """Dashboard data aggregator"""
    
    def __init__(self, app):
        self.app = app
    
    def get_trading_stats(self) -> Dict[str, Any]:
        """Get trading statistics"""
        trades = self.app.db.get_trades(limit=50)
        if not trades:
            return {'status': 'no_trades'}
        
        total_trades = len(trades)
        winning = sum(1 for t in trades if t[6] > 0)  # profit_loss
        losing = total_trades - winning
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning,
            'losing_trades': losing,
            'win_rate': (winning / total_trades * 100) if total_trades > 0 else 0,
            'total_profit': sum(t[6] for t in trades)
        }
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get AI model status"""
        return {
            'available_models': self.app.available_models,
            'skills': self.app.skill_system.get_all_skills(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {'status': 'monitoring_unavailable'}
    
    def get_full_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            'trading': self.get_trading_stats(),
            'ai': self.get_ai_status(),
            'system': self.get_system_health(),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    logger.info("Dashboard data aggregator ready")
