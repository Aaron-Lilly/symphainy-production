#!/usr/bin/env python3
"""Embedding creation module for Semantic Enrichment Service."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import pandas as pd
import numpy as np
from scipy import stats


class EmbeddingCreation:
    """Embedding creation module for Semantic Enrichment Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def get_parsed_file(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get parsed file from Content Steward (SECURE BOUNDARY - ONLY place this happens).
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context
            
        Returns:
            Parsed file dict or None if not found
        """
        try:
            if not self.service.librarian:
                self.logger.error("❌ Librarian API not available")
                return None
            
            if not self.service.content_steward:
                self.logger.error("❌ Content Steward API not available")
                return None
            
            # Get content metadata to find parsed_file_id
            content_metadata = await self.service.librarian.get_content_metadata(
                content_id,
                user_context
            )
            
            if not content_metadata:
                self.logger.warning(f"⚠️ Content metadata not found for content_id: {content_id}")
                return None
            
            parsed_file_id = content_metadata.get("parsed_file_id")
            if not parsed_file_id:
                self.logger.warning(f"⚠️ parsed_file_id not found in content metadata for content_id: {content_id}")
                return None
            
            # Get parsed file (SECURE BOUNDARY - ONLY place this happens)
            parsed_file = await self.service.content_steward.get_file(
                parsed_file_id,
                user_context
            )
            
            if not parsed_file:
                self.logger.warning(f"⚠️ Parsed file not found for parsed_file_id: {parsed_file_id}")
                return None
            
            self.logger.info(f"✅ Retrieved parsed file for content_id: {content_id}")
            return parsed_file
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get parsed file: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    async def create_column_value_embeddings(
        self,
        parsed_file: Dict[str, Any],
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create embeddings for specific column values.
        
        Args:
            parsed_file: Parsed file dict
            content_id: Content metadata ID
            filters: Optional filters (which columns needed)
            user_context: Optional user context
            
        Returns:
            List of new embeddings
        """
        try:
            # Parse to DataFrame
            df = self.service.utilities_module.parse_parsed_file_to_dataframe(parsed_file)
            if df is None or df.empty:
                self.logger.warning("⚠️ Failed to parse parsed file to DataFrame or DataFrame is empty")
                return []
            
            # Apply filters
            df = self.service.utilities_module.filter_dataframe(df, filters)
            
            # Create embeddings for each column
            embeddings = []
            columns_to_process = filters.get("columns", df.columns.tolist()) if filters else df.columns.tolist()
            
            for column in columns_to_process:
                if column not in df.columns:
                    continue
                
                # Get sample values (representative sampling)
                column_data = df[column].dropna()
                if len(column_data) == 0:
                    continue
                
                # Sample values (every nth value for representative sampling)
                sample_size = min(100, len(column_data))
                step = max(1, len(column_data) // sample_size)
                sample_values = column_data.iloc[::step].tolist()[:sample_size]
                
                # Create embedding
                embedding = {
                    "_key": f"enrich_colval_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "id": f"enrich_colval_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "content_id": content_id,
                    "column_name": column,
                    "embedding_type": "column_values",
                    "metadata": {
                        "data_type": str(df[column].dtype),
                        "total_count": len(df[column]),
                        "non_null_count": len(column_data),
                        "null_count": len(df[column]) - len(column_data),
                        "sample_size": len(sample_values)
                    },
                    "sample_values": sample_values[:10],  # Store first 10 for preview
                    "created_at": datetime.now().isoformat(),
                    "enrichment_type": "column_values"
                }
                
                embeddings.append(embedding)
            
            self.logger.info(f"✅ Created {len(embeddings)} column value embeddings")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create column value embeddings: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return []
    
    async def create_statistics_embeddings(
        self,
        parsed_file: Dict[str, Any],
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create embeddings for statistics.
        
        Args:
            parsed_file: Parsed file dict
            content_id: Content metadata ID
            filters: Optional filters (which columns needed)
            user_context: Optional user context
            
        Returns:
            List of new embeddings
        """
        try:
            # Parse to DataFrame
            df = self.service.utilities_module.parse_parsed_file_to_dataframe(parsed_file)
            if df is None or df.empty:
                return []
            
            # Apply filters
            df = self.service.utilities_module.filter_dataframe(df, filters)
            
            # Create embeddings for numerical columns
            embeddings = []
            columns_to_process = filters.get("columns", df.select_dtypes(include=[np.number]).columns.tolist()) if filters else df.select_dtypes(include=[np.number]).columns.tolist()
            
            for column in columns_to_process:
                if column not in df.columns:
                    continue
                
                column_data = df[column].dropna()
                if len(column_data) == 0:
                    continue
                
                # Calculate statistics
                stats_dict = {
                    "mean": float(column_data.mean()) if pd.api.types.is_numeric_dtype(column_data) else None,
                    "median": float(column_data.median()) if pd.api.types.is_numeric_dtype(column_data) else None,
                    "std": float(column_data.std()) if pd.api.types.is_numeric_dtype(column_data) else None,
                    "min": float(column_data.min()) if pd.api.types.is_numeric_dtype(column_data) else None,
                    "max": float(column_data.max()) if pd.api.types.is_numeric_dtype(column_data) else None,
                    "count": len(column_data),
                    "null_count": len(df[column]) - len(column_data),
                    "skewness": float(stats.skew(column_data)) if pd.api.types.is_numeric_dtype(column_data) and len(column_data) > 2 else None,
                    "kurtosis": float(stats.kurtosis(column_data)) if pd.api.types.is_numeric_dtype(column_data) and len(column_data) > 2 else None
                }
                
                # Create embedding
                embedding = {
                    "_key": f"enrich_stats_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "id": f"enrich_stats_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "content_id": content_id,
                    "column_name": column,
                    "embedding_type": "statistics",
                    "metadata": stats_dict,
                    "created_at": datetime.now().isoformat(),
                    "enrichment_type": "statistics"
                }
                
                embeddings.append(embedding)
            
            self.logger.info(f"✅ Created {len(embeddings)} statistics embeddings")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create statistics embeddings: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return []
    
    async def create_correlation_embeddings(
        self,
        parsed_file: Dict[str, Any],
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Create embeddings for correlations."""
        # Similar pattern to statistics - calculate correlations between numerical columns
        try:
            df = self.service.utilities_module.parse_parsed_file_to_dataframe(parsed_file)
            if df is None or df.empty:
                return []
            
            df = self.service.utilities_module.filter_dataframe(df, filters)
            
            # Calculate correlation matrix for numerical columns
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numerical_cols) < 2:
                return []
            
            corr_matrix = df[numerical_cols].corr()
            
            # Create embedding for correlation matrix
            embedding = {
                "_key": f"enrich_corr_{content_id}_{uuid.uuid4().hex[:8]}",
                "id": f"enrich_corr_{content_id}_{uuid.uuid4().hex[:8]}",
                "content_id": content_id,
                "embedding_type": "correlations",
                "metadata": {
                    "correlation_matrix": corr_matrix.to_dict(),
                    "columns": numerical_cols
                },
                "created_at": datetime.now().isoformat(),
                "enrichment_type": "correlations"
            }
            
            self.logger.info("✅ Created correlation embeddings")
            return [embedding]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create correlation embeddings: {e}")
            return []
    
    async def create_distribution_embeddings(
        self,
        parsed_file: Dict[str, Any],
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Create embeddings for distributions."""
        # Similar pattern - calculate distribution metrics
        try:
            df = self.service.utilities_module.parse_parsed_file_to_dataframe(parsed_file)
            if df is None or df.empty:
                return []
            
            df = self.service.utilities_module.filter_dataframe(df, filters)
            
            embeddings = []
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            for column in numerical_cols:
                column_data = df[column].dropna()
                if len(column_data) == 0:
                    continue
                
                # Calculate quartiles
                quartiles = column_data.quantile([0.25, 0.5, 0.75]).to_dict()
                
                embedding = {
                    "_key": f"enrich_dist_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "id": f"enrich_dist_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "content_id": content_id,
                    "column_name": column,
                    "embedding_type": "distributions",
                    "metadata": {
                        "quartiles": quartiles,
                        "skewness": float(stats.skew(column_data)) if len(column_data) > 2 else None,
                        "kurtosis": float(stats.kurtosis(column_data)) if len(column_data) > 2 else None
                    },
                    "created_at": datetime.now().isoformat(),
                    "enrichment_type": "distributions"
                }
                
                embeddings.append(embedding)
            
            self.logger.info(f"✅ Created {len(embeddings)} distribution embeddings")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create distribution embeddings: {e}")
            return []
    
    async def create_missing_value_embeddings(
        self,
        parsed_file: Dict[str, Any],
        content_id: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Create embeddings for missing values analysis."""
        try:
            df = self.service.utilities_module.parse_parsed_file_to_dataframe(parsed_file)
            if df is None or df.empty:
                return []
            
            df = self.service.utilities_module.filter_dataframe(df, filters)
            
            embeddings = []
            
            for column in df.columns:
                null_count = df[column].isna().sum()
                total_count = len(df[column])
                
                embedding = {
                    "_key": f"enrich_missing_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "id": f"enrich_missing_{content_id}_{column}_{uuid.uuid4().hex[:8]}",
                    "content_id": content_id,
                    "column_name": column,
                    "embedding_type": "missing_values",
                    "metadata": {
                        "total_count": total_count,
                        "null_count": int(null_count),
                        "missing_percentage": float((null_count / total_count) * 100) if total_count > 0 else 0.0,
                        "has_missing": null_count > 0
                    },
                    "created_at": datetime.now().isoformat(),
                    "enrichment_type": "missing_values"
                }
                
                embeddings.append(embedding)
            
            self.logger.info(f"✅ Created {len(embeddings)} missing value embeddings")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create missing value embeddings: {e}")
            return []

