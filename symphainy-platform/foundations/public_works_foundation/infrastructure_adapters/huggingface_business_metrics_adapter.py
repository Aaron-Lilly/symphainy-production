#!/usr/bin/env python3
"""
HuggingFace Business Metrics Adapter

Infrastructure adapter for AI-powered business metrics analysis using HuggingFace models.

WHAT (Infrastructure Adapter Role): I provide AI-powered business metrics analysis capabilities
HOW (Adapter Implementation): I wrap HuggingFace models for advanced metrics insights and predictions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

# HuggingFace Transformers imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️ HuggingFace Transformers not available. Install with: pip install transformers torch")

from ..abstraction_contracts.business_metrics_protocol import BusinessMetricsResult


class HuggingFaceBusinessMetricsAdapter:
    """
    HuggingFace Business Metrics Adapter
    
    Provides AI-powered business metrics analysis capabilities using HuggingFace models.
    """
    
    def __init__(self):
        """Initialize HuggingFace Business Metrics Adapter."""
        self.logger = logging.getLogger("HuggingFaceBusinessMetricsAdapter")
        self.hf_available = HF_AVAILABLE
        self.sentiment_pipeline = None
        self.text_generation_pipeline = None
        self.classification_pipeline = None
        self.is_initialized = False
        self.logger.info("🏗️ HuggingFaceBusinessMetricsAdapter initialized")
    
    async def initialize_models(self):
        """Initialize HuggingFace models."""
        if not self.hf_available:
            self.logger.warning("HuggingFace Transformers not available - using fallback implementations")
            return
        
        try:
            self.logger.info("Loading HuggingFace models for business metrics analysis...")
            
            # Load sentiment analysis model for business text
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
            
            # Load text generation model for business insights
            self.text_generation_pipeline = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium"
            )
            
            # Load classification model for business document analysis
            self.classification_pipeline = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            self.is_initialized = True
            self.logger.info("✅ HuggingFace models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load HuggingFace models: {e}")
            self.is_initialized = False
            raise
    
    async def analyze_business_sentiment(self, business_data: Dict[str, Any]) -> BusinessMetricsResult:
        """
        Analyze business sentiment using AI models.
        
        Args:
            business_data: Business data for sentiment analysis
            
        Returns:
            BusinessMetricsResult: Result of the sentiment analysis
        """
        try:
            self.logger.info("Analyzing business sentiment using HuggingFace models...")
            
            if not self.is_initialized:
                await self.initialize_models()
            
            # Create business context text for analysis
            business_context = self._create_business_context_text(business_data)
            
            # Use HuggingFace models for real analysis
            if self.hf_available and self.is_initialized:
                # Analyze sentiment of business context
                sentiment_result = self.sentiment_pipeline(business_context)
                sentiment_score = sentiment_result[0]['score'] if sentiment_result else 0.5
                sentiment_label = sentiment_result[0]['label'] if sentiment_result else 'NEUTRAL'
                
                # Generate business insights using text generation
                insight_prompt = f"Analyze the business performance and sentiment: {business_context[:200]}"
                business_insights = self.text_generation_pipeline(
                    insight_prompt, 
                    max_length=150, 
                    num_return_sequences=1,
                    temperature=0.7
                )
                
                # Classify business performance factors
                performance_categories = ["financial_health", "operational_efficiency", "market_position", "growth_potential"]
                classification_result = self.classification_pipeline(
                    business_context, 
                    candidate_labels=performance_categories
                )
                
                # Calculate AI-powered business score
                business_score = self._calculate_ai_business_score(sentiment_score, classification_result)
                performance_level = self._classify_performance_level(business_score)
                ai_insights = self._extract_ai_insights(business_insights, classification_result)
                
            else:
                # Fallback to basic analysis if HuggingFace not available
                business_score = self._calculate_fallback_business_score(business_data)
                performance_level = self._classify_performance_level(business_score)
                ai_insights = self._generate_fallback_insights(business_data)
            
            return BusinessMetricsResult(
                success=True,
                ai_analysis={
                    "business_score": business_score,
                    "performance_level": performance_level,
                    "sentiment_score": sentiment_score if self.hf_available and self.is_initialized else 0.5,
                    "sentiment_label": sentiment_label if self.hf_available and self.is_initialized else "neutral"
                },
                insights=ai_insights,
                recommendations=self._generate_ai_recommendations(business_score, ai_insights),
                metadata={
                    "analysis_method": "huggingface_ai" if self.hf_available and self.is_initialized else "fallback",
                    "model_version": "finbert-sentiment-v1.0" if self.hf_available else "basic-analysis-v1.0",
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze business sentiment: {e}")
            return BusinessMetricsResult(
                success=False,
                ai_analysis={},
                insights=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def predict_business_performance(self, historical_data: List[Dict[str, Any]]) -> BusinessMetricsResult:
        """
        Predict business performance using AI models.
        
        Args:
            historical_data: Historical business data for prediction
            
        Returns:
            BusinessMetricsResult: Result of the performance prediction
        """
        try:
            self.logger.info("Predicting business performance using HuggingFace models...")
            
            if not self.is_initialized:
                await self.initialize_models()
            
            # Create historical context text
            historical_context = self._create_historical_context_text(historical_data)
            
            # Use AI for performance prediction
            if self.hf_available and self.is_initialized:
                # Generate performance predictions
                prediction_prompt = f"Predict future business performance based on: {historical_context[:200]}"
                performance_predictions = self.text_generation_pipeline(
                    prediction_prompt,
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.6
                )
                
                # Analyze performance trends
                trend_categories = ["growth_trend", "stability_trend", "decline_trend", "volatility_trend"]
                trend_analysis = self.classification_pipeline(
                    historical_context,
                    candidate_labels=trend_categories
                )
                
                # Generate AI predictions
                predictions = self._generate_ai_predictions(performance_predictions, trend_analysis)
                confidence_score = self._calculate_prediction_confidence(trend_analysis)
                
            else:
                # Fallback predictions
                predictions = self._generate_fallback_predictions(historical_data)
                confidence_score = 0.5
            
            return BusinessMetricsResult(
                success=True,
                predictions=predictions,
                confidence_score=confidence_score,
                insights=self._generate_prediction_insights(predictions, confidence_score),
                recommendations=self._generate_prediction_recommendations(predictions),
                metadata={
                    "prediction_method": "huggingface_ai" if self.hf_available and self.is_initialized else "fallback",
                    "model_version": "business-prediction-v1.0" if self.hf_available else "basic-prediction-v1.0",
                    "predicted_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to predict business performance: {e}")
            return BusinessMetricsResult(
                success=False,
                predictions={},
                confidence_score=0,
                insights=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def generate_business_insights(self, business_data: Dict[str, Any]) -> BusinessMetricsResult:
        """
        Generate AI-powered business insights.
        
        Args:
            business_data: Business data for insight generation
            
        Returns:
            BusinessMetricsResult: Result of the insight generation
        """
        try:
            self.logger.info("Generating AI-powered business insights...")
            
            if not self.is_initialized:
                await self.initialize_models()
            
            # Create business context for insight generation
            business_context = self._create_business_context_text(business_data)
            
            # Use AI to generate insights
            if self.hf_available and self.is_initialized:
                # Generate comprehensive business insights
                insight_prompt = f"Generate strategic business insights for: {business_context[:200]}"
                ai_insights = self.text_generation_pipeline(
                    insight_prompt,
                    max_length=300,
                    num_return_sequences=1,
                    temperature=0.8
                )
                
                # Classify business opportunities
                opportunity_categories = ["cost_optimization", "revenue_growth", "market_expansion", "operational_improvement"]
                opportunity_analysis = self.classification_pipeline(
                    business_context,
                    candidate_labels=opportunity_categories
                )
                
                # Extract insights and opportunities
                insights = self._extract_ai_insights(ai_insights, opportunity_analysis)
                opportunities = self._identify_business_opportunities(opportunity_analysis)
                
            else:
                # Fallback insights
                insights = self._generate_fallback_insights(business_data)
                opportunities = self._identify_fallback_opportunities(business_data)
            
            return BusinessMetricsResult(
                success=True,
                insights=insights,
                opportunities=opportunities,
                recommendations=self._generate_opportunity_recommendations(opportunities),
                metadata={
                    "insight_method": "huggingface_ai" if self.hf_available and self.is_initialized else "fallback",
                    "model_version": "business-insights-v1.0" if self.hf_available else "basic-insights-v1.0",
                    "generated_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate business insights: {e}")
            return BusinessMetricsResult(
                success=False,
                insights=[],
                opportunities=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the adapter."""
        try:
            if not self.is_initialized:
                await self.initialize_models()
            
            return {
                "status": "healthy" if self.hf_available else "limited",
                "adapter": "HuggingFaceBusinessMetricsAdapter",
                "hf_available": self.hf_available,
                "is_initialized": self.is_initialized,
                "capabilities": [
                    "business_sentiment_analysis",
                    "performance_prediction",
                    "insight_generation"
                ],
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter": "HuggingFaceBusinessMetricsAdapter",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _create_business_context_text(self, business_data: Dict[str, Any]) -> str:
        """Create business context text for AI analysis."""
        context_parts = []
        
        if "revenue" in business_data:
            context_parts.append(f"Revenue: ${business_data['revenue']:,}")
        
        if "profit_margin" in business_data:
            context_parts.append(f"Profit margin: {business_data['profit_margin']}%")
        
        if "growth_rate" in business_data:
            context_parts.append(f"Growth rate: {business_data['growth_rate']}%")
        
        if "customer_satisfaction" in business_data:
            context_parts.append(f"Customer satisfaction: {business_data['customer_satisfaction']}%")
        
        if "market_share" in business_data:
            context_parts.append(f"Market share: {business_data['market_share']}%")
        
        return ". ".join(context_parts)
    
    def _create_historical_context_text(self, historical_data: List[Dict[str, Any]]) -> str:
        """Create historical context text for AI analysis."""
        if not historical_data:
            return "No historical data available"
        
        # Summarize historical trends
        context_parts = []
        for i, data_point in enumerate(historical_data[-5:]):  # Last 5 data points
            if "revenue" in data_point:
                context_parts.append(f"Period {i+1}: Revenue ${data_point['revenue']:,}")
        
        return ". ".join(context_parts)
    
    def _calculate_ai_business_score(self, sentiment_score: float, classification_result: Dict[str, Any]) -> float:
        """Calculate AI-powered business score."""
        # Combine sentiment and classification results
        sentiment_contribution = sentiment_score * 0.6
        
        # Get top classification score
        top_score = max(classification_result.get('scores', [0]))
        classification_contribution = top_score * 0.4
        
        # Weighted combination
        business_score = (sentiment_contribution + classification_contribution) * 100
        
        return min(100, max(0, business_score))
    
    def _classify_performance_level(self, business_score: float) -> str:
        """Classify performance level based on score."""
        if business_score >= 80:
            return "excellent"
        elif business_score >= 65:
            return "good"
        elif business_score >= 50:
            return "average"
        elif business_score >= 35:
            return "below_average"
        else:
            return "poor"
    
    def _extract_ai_insights(self, ai_insights: List[Dict], classification_result: Dict[str, Any]) -> List[str]:
        """Extract insights from AI analysis results."""
        insights = []
        
        # Extract from generated insights
        if ai_insights and len(ai_insights) > 0:
            generated_text = ai_insights[0].get('generated_text', '')
            if len(generated_text) > 50:  # Filter out very short responses
                insights.append(f"AI Analysis: {generated_text[:200]}...")
        
        # Extract from classification results
        labels = classification_result.get('labels', [])
        scores = classification_result.get('scores', [])
        
        for label, score in zip(labels, scores):
            if score > 0.6:  # High confidence
                insights.append(f"Strong {label.replace('_', ' ')} identified by AI")
        
        return insights
    
    def _generate_ai_recommendations(self, business_score: float, insights: List[str]) -> List[str]:
        """Generate AI-powered recommendations."""
        recommendations = []
        
        if business_score < 50:
            recommendations.append("Focus on improving core business metrics")
            recommendations.append("Consider strategic pivots or operational changes")
        elif business_score < 75:
            recommendations.append("Maintain current performance and identify growth opportunities")
        else:
            recommendations.append("Leverage strong performance for expansion")
        
        return recommendations
    
    def _calculate_fallback_business_score(self, business_data: Dict[str, Any]) -> float:
        """Calculate fallback business score when AI not available."""
        # Simple weighted average of available metrics
        metrics = []
        
        if "profit_margin" in business_data:
            metrics.append(business_data["profit_margin"])
        
        if "growth_rate" in business_data:
            metrics.append(max(0, business_data["growth_rate"]))
        
        if "customer_satisfaction" in business_data:
            metrics.append(business_data["customer_satisfaction"])
        
        return sum(metrics) / len(metrics) if metrics else 50.0
    
    def _generate_fallback_insights(self, business_data: Dict[str, Any]) -> List[str]:
        """Generate fallback insights when AI not available."""
        insights = []
        
        if business_data.get("profit_margin", 0) > 15:
            insights.append("Strong profit margins indicate healthy financial performance")
        
        if business_data.get("growth_rate", 0) > 10:
            insights.append("High growth rate suggests strong market position")
        
        return insights
    
    def _generate_ai_predictions(self, performance_predictions: List[Dict], trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered predictions."""
        predictions = {
            "revenue_growth": 0.0,
            "profit_margin": 0.0,
            "market_share": 0.0,
            "confidence": 0.0
        }
        
        # Extract predictions from AI-generated text
        if performance_predictions and len(performance_predictions) > 0:
            generated_text = performance_predictions[0].get('generated_text', '')
            # Simple extraction (in real implementation, this would be more sophisticated)
            if "growth" in generated_text.lower():
                predictions["revenue_growth"] = 5.0  # Default positive growth
                predictions["confidence"] = 0.7
        
        # Use trend analysis for additional predictions
        top_trend = max(trend_analysis.get('scores', [0]))
        if top_trend > 0.5:
            predictions["confidence"] = top_trend
        
        return predictions
    
    def _calculate_prediction_confidence(self, trend_analysis: Dict[str, Any]) -> float:
        """Calculate prediction confidence based on trend analysis."""
        scores = trend_analysis.get('scores', [])
        return max(scores) if scores else 0.5
    
    def _generate_prediction_insights(self, predictions: Dict[str, Any], confidence: float) -> List[str]:
        """Generate insights from predictions."""
        insights = []
        
        if confidence > 0.7:
            insights.append("High confidence in predictions based on strong trend analysis")
        elif confidence > 0.5:
            insights.append("Moderate confidence in predictions")
        else:
            insights.append("Low confidence in predictions - more data needed")
        
        return insights
    
    def _generate_prediction_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on predictions."""
        recommendations = []
        
        if predictions.get("revenue_growth", 0) > 0:
            recommendations.append("Prepare for growth by scaling operations")
        else:
            recommendations.append("Focus on revenue growth strategies")
        
        return recommendations
    
    def _identify_business_opportunities(self, opportunity_analysis: Dict[str, Any]) -> List[str]:
        """Identify business opportunities from AI analysis."""
        opportunities = []
        
        labels = opportunity_analysis.get('labels', [])
        scores = opportunity_analysis.get('scores', [])
        
        for label, score in zip(labels, scores):
            if score > 0.6:  # High confidence
                opportunities.append(f"AI-identified opportunity: {label.replace('_', ' ')}")
        
        return opportunities
    
    def _identify_fallback_opportunities(self, business_data: Dict[str, Any]) -> List[str]:
        """Identify fallback opportunities when AI not available."""
        opportunities = []
        
        if business_data.get("profit_margin", 0) < 10:
            opportunities.append("Cost optimization opportunity")
        
        if business_data.get("growth_rate", 0) < 5:
            opportunities.append("Revenue growth opportunity")
        
        return opportunities
    
    def _generate_opportunity_recommendations(self, opportunities: List[str]) -> List[str]:
        """Generate recommendations based on opportunities."""
        recommendations = []
        
        for opportunity in opportunities:
            if "cost optimization" in opportunity.lower():
                recommendations.append("Implement cost reduction initiatives")
            elif "revenue growth" in opportunity.lower():
                recommendations.append("Develop new revenue streams")
        
        return recommendations
    
    def _generate_fallback_predictions(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback predictions when AI not available."""
        predictions = {
            "revenue_growth": 0.0,
            "profit_margin": 0.0,
            "market_share": 0.0,
            "confidence": 0.5
        }
        
        if len(historical_data) >= 2:
            # Simple trend-based predictions
            latest = historical_data[-1]
            previous = historical_data[-2]
            
            # Calculate growth trends
            if "revenue" in latest and "revenue" in previous:
                revenue_growth = ((latest["revenue"] - previous["revenue"]) / previous["revenue"]) * 100
                predictions["revenue_growth"] = max(0, revenue_growth)
            
            if "profit" in latest and "revenue" in latest and latest["revenue"] > 0:
                profit_margin = (latest["profit"] / latest["revenue"]) * 100
                predictions["profit_margin"] = max(0, profit_margin)
        
        return predictions
