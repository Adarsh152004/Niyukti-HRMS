"""
AI-Powered Intelligent HRMS — Analytics Package.
"""

from backend.analytics.router import router
from backend.analytics.service import ExecutiveDashboardMetrics, KPIService

__all__ = [
    "KPIService",
    "ExecutiveDashboardMetrics",
    "router",
]
