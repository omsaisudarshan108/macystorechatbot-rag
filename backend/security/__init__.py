"""
Infrastructure Security Module

Prevents disclosure of backend infrastructure details and hosting information.
"""

from .infrastructure_guard import InfrastructureSecurityGuard

__all__ = ['InfrastructureSecurityGuard']
