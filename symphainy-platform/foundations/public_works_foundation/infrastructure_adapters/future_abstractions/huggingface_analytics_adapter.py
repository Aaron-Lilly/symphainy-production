"""
HuggingFace Analytics Adapter - Swappable infrastructure for advanced analytics
Provides HuggingFace model integration for insights generation capabilities.
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

# HuggingFace imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    from transformers import TextClassificationPipeline, SummarizationPipeline
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    pipeline = None
    AutoTokenizer = None
    AutoModel = None
    TextClassificationPipeline = None
    SummarizationPipeline = None

from ..abstraction_contracts.data_analysis_protocol import DataAnalysisProtocol
from ..abstraction_contracts.insights_generation_protocol import InsightsGenerationProtocol

logger = logging.getLogger(__name__)

@dataclass
class HuggingFaceModelConfig:
    """Configuration for HuggingFace models."""
    model_name: str
    task_type: str
    max_length: int = 512
    temperature: float = 0.7
    device: str = "cpu"

class HuggingFaceAnalyticsAdapter:
    """
    HuggingFace Analytics Adapter - Swappable infrastructure for advanced analytics.
    Provides HuggingFace model integration for insights generation capabilities.
    """
    
    def __init__(self, model_configs: Dict[str, HuggingFaceModelConfig] = None):
        """
        Initialize HuggingFace Analytics Adapter.
        
        Args:
            model_configs: Dictionary of model configurations
        """
        self.model_configs = model_configs or self._get_default_model_configs()
        self.pipelines = {}
        self.initialized = False
        
        if not HUGGINGFACE_AVAILABLE:
            logger.warning("HuggingFace transformers not available. Adapter will be limited.")
    
    def _get_default_model_configs(self) -> Dict[str, HuggingFaceModelConfig]:
        """Get default model configurations."""
        return {
            "sentiment_analysis": HuggingFaceModelConfig(
                model_name="cardiffnlp/twitter-roberta-base-sentiment-latest",
                task_type="sentiment-analysis"
            ),
            "text_classification": HuggingFaceModelConfig(
                model_name="distilbert-base-uncased",
                task_type="text-classification"
            ),
            "summarization": HuggingFaceModelConfig(
                model_name="facebook/bart-large-cnn",
                task_type="summarization"
            ),
            "question_answering": HuggingFaceModelConfig(
                model_name="distilbert-base-cased-distilled-squad",
                task_type="question-answering"
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize HuggingFace models and pipelines."""
        if not HUGGINGFACE_AVAILABLE:
            logger.error("HuggingFace transformers not available")
            return False
        
        try:
            for model_name, config in self.model_configs.items():
                logger.info(f"Loading HuggingFace model: {config.model_name}")
                
                # Create pipeline for the model
                pipeline_instance = pipeline(
                    config.task_type,
                    model=config.model_name,
                    device=config.device
                )
                
                self.pipelines[model_name] = pipeline_instance
                logger.info(f"Successfully loaded model: {model_name}")
            
            self.initialized = True
            logger.info("HuggingFace Analytics Adapter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace models: {e}")
            return False
    
    async def analyze_sentiment(self, text: str, user_context: Any = None) -> Dict[str, Any]:
        """
        Analyze sentiment of text using HuggingFace models.
        
        Args:
            text: Text to analyze
            user_context: User context for analysis
            
        Returns:
            Sentiment analysis results
        """
        if not self.initialized or "sentiment_analysis" not in self.pipelines:
            return {"error": "Sentiment analysis model not available"}
        
        try:
            pipeline = self.pipelines["sentiment_analysis"]
            result = pipeline(text)
            
            return {
                "sentiment": result[0]["label"],
                "confidence": result[0]["score"],
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model_configs["sentiment_analysis"].model_name
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": str(e)}
    
    async def classify_text(self, text: str, categories: List[str] = None, user_context: Any = None) -> Dict[str, Any]:
        """
        Classify text using HuggingFace models.
        
        Args:
            text: Text to classify
            categories: Optional categories to focus on
            user_context: User context for analysis
            
        Returns:
            Text classification results
        """
        if not self.initialized or "text_classification" not in self.pipelines:
            return {"error": "Text classification model not available"}
        
        try:
            pipeline = self.pipelines["text_classification"]
            result = pipeline(text)
            
            return {
                "classification": result[0]["label"],
                "confidence": result[0]["score"],
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model_configs["text_classification"].model_name
            }
        except Exception as e:
            logger.error(f"Text classification failed: {e}")
            return {"error": str(e)}
    
    async def summarize_text(self, text: str, max_length: int = 150, user_context: Any = None) -> Dict[str, Any]:
        """
        Summarize text using HuggingFace models.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            user_context: User context for analysis
            
        Returns:
            Text summarization results
        """
        if not self.initialized or "summarization" not in self.pipelines:
            return {"error": "Summarization model not available"}
        
        try:
            pipeline = self.pipelines["summarization"]
            result = pipeline(text, max_length=max_length)
            
            return {
                "summary": result[0]["summary_text"],
                "original_length": len(text),
                "summary_length": len(result[0]["summary_text"]),
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model_configs["summarization"].model_name
            }
        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return {"error": str(e)}
    
    async def answer_question(self, question: str, context: str, user_context: Any = None) -> Dict[str, Any]:
        """
        Answer questions using HuggingFace models.
        
        Args:
            question: Question to answer
            context: Context for answering
            user_context: User context for analysis
            
        Returns:
            Question answering results
        """
        if not self.initialized or "question_answering" not in self.pipelines:
            return {"error": "Question answering model not available"}
        
        try:
            pipeline = self.pipelines["question_answering"]
            result = pipeline(question=question, context=context)
            
            return {
                "answer": result["answer"],
                "confidence": result["score"],
                "start_position": result["start"],
                "end_position": result["end"],
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.model_configs["question_answering"].model_name
            }
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            return {"error": str(e)}
    
    async def generate_insights(self, data: Dict[str, Any], user_context: Any = None) -> Dict[str, Any]:
        """
        Generate insights using HuggingFace models.
        
        Args:
            data: Data to analyze for insights
            user_context: User context for analysis
            
        Returns:
            Generated insights
        """
        if not self.initialized:
            return {"error": "HuggingFace models not initialized"}
        
        try:
            insights = []
            
            # Analyze text data if present
            if "text_data" in data:
                text_data = data["text_data"]
                
                # Sentiment analysis
                sentiment_result = await self.analyze_sentiment(text_data, user_context)
                if "error" not in sentiment_result:
                    insights.append({
                        "type": "sentiment",
                        "value": sentiment_result["sentiment"],
                        "confidence": sentiment_result["confidence"]
                    })
                
                # Text classification
                classification_result = await self.classify_text(text_data, user_context=user_context)
                if "error" not in classification_result:
                    insights.append({
                        "type": "classification",
                        "value": classification_result["classification"],
                        "confidence": classification_result["confidence"]
                    })
                
                # Summarization
                summary_result = await self.summarize_text(text_data, user_context=user_context)
                if "error" not in summary_result:
                    insights.append({
                        "type": "summary",
                        "value": summary_result["summary"]
                    })
            
            return {
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat(),
                "models_used": list(self.model_configs.keys())
            }
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of HuggingFace Analytics Adapter."""
        return {
            "status": "healthy" if self.initialized else "unhealthy",
            "initialized": self.initialized,
            "models_loaded": len(self.pipelines),
            "available_models": list(self.pipelines.keys()),
            "huggingface_available": HUGGINGFACE_AVAILABLE,
            "timestamp": datetime.utcnow().isoformat()
        }




