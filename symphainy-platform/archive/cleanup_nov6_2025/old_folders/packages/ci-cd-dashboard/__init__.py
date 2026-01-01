"""
CI/CD Dashboard Package
Comprehensive admin dashboard for CI/CD monitoring and platform governance
"""

__version__ = "1.0.0"
__author__ = "SymphAIny Platform Team"

from .ci_cd_dashboard_service import CICDDashboardService
from .ci_cd_dashboard_mcp_server import CICDDashboardMCPServer

__all__ = [
    "CICDDashboardService",
    "CICDDashboardMCPServer"
]




