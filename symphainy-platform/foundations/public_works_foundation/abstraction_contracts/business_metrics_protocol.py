#!/usr/bin/env python3
"""
Business Metrics Protocol

Abstraction contract for business metrics capabilities.

WHAT (Protocol Role): I define the contract for business metrics analysis
HOW (Protocol Implementation): I specify the interface for KPI calculation, benchmarking, and performance analysis
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BusinessMetricsResult:
    """
    Business Metrics Result
    
    Standardized result structure for business metrics operations.
    """
    success: bool
    kpis: Optional[Dict[str, Any]] = None
    benchmark_results: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    overall_benchmark_score: Optional[float] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BusinessMetricsProtocol(Protocol):
    """
    Business Metrics Protocol
    
    Defines the contract for business metrics analysis capabilities.
    """
    
    async def calculate_kpis(self, business_data: Dict[str, Any]) -> BusinessMetricsResult:
        """
        Calculate Key Performance Indicators (KPIs).
        
        Args:
            business_data: Business data for KPI calculation
            
        Returns:
            BusinessMetricsResult: Result of the KPI calculation
        """
        ...
    
    async def benchmark_performance(self, metrics_data: Dict[str, Any], industry: str = "default") -> BusinessMetricsResult:
        """
        Benchmark performance against industry standards.
        
        Args:
            metrics_data: Business metrics data
            industry: Industry for benchmarking
            
        Returns:
            BusinessMetricsResult: Result of the benchmarking
        """
        ...
    
    async def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> BusinessMetricsResult:
        """
        Analyze business trends from historical data.
        
        Args:
            historical_data: Historical business data
            
        Returns:
            BusinessMetricsResult: Result of the trend analysis
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the business metrics service.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        ...
