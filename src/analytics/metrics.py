from typing import Dict, Any
from src.database.models import AnalyticsRepository

class AnalyticsEngine:
    """Calculates and aggregates knowledge base metrics, category distributions, and query stats."""
    
    @staticmethod
    def get_dashboard_analytics() -> Dict[str, Any]:
        return AnalyticsRepository.get_system_metrics()
