#!/usr/bin/env python3
"""Embedding creation module for Embedding Service."""

import io
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class EmbeddingCreation:
    """Embedding creation module for Embedding Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def _infer_semantic_meaning(
        self,
        column_name: str,
        data_type: str,
        sample_values: List[str]
    ) -> str:
        """
        Infer semantic meaning of a column using agent-based LLM reasoning.
        
        CRITICAL: Uses agent via Agentic Foundation SDK (NO direct LLM access).
        This enforces governance, traceability, and cost control.
        
        Uses agent to analyze column name, data type, and sample values
        to infer the semantic meaning of the column.
        
        Args:
            column_name: Column name
            data_type: Column data type
            sample_values: List of sample values (first 5)
        
        Returns:
            Semantic meaning text (e.g., "Customer email address" instead of just "email")
        """
        try:
            if not self.service.semantic_meaning_agent:
                # Fallback to column name if agent not available
                return f"Column: {column_name}"
            
            # Use agent for semantic meaning inference (via Agentic Foundation SDK)
            # CRITICAL: Use agent's _call_llm_simple method which handles tracking and governance
            system_message = """You are a data analyst inferring the semantic meaning of database columns.

Analyze the column name, data type, and sample values to determine what the column represents.

Return ONLY a concise description (1-5 words) of what the column represents.
Examples:
- "email" -> "Customer email address"
- "created_at" -> "Record creation timestamp"
- "amount" -> "Transaction amount"
- "status" -> "Order status code"

Be specific and descriptive."""
            
            samples_str = ', '.join(sample_values[:5]) if sample_values else "no samples"
            user_prompt = f"""Column name: {column_name}
Data type: {data_type}
Sample values: {samples_str}

What does this column represent? Return ONLY a concise description (1-5 words)."""
            
            # Use agent's _call_llm_simple method (via Agentic Foundation SDK)
            # This ensures proper governance, traceability, and cost control
            try:
                # Use agent's async LLM call method with tracking
                response_text = await self.service.semantic_meaning_agent._call_llm_simple(
                    prompt=user_prompt,
                    system_message=system_message,
                    model="gpt-4o-mini",
                    max_tokens=30,
                    temperature=0.3,
                    user_context=None,
                    metadata={"task": "infer_semantic_meaning", "column": column_name}
                )
                
                # Clean up response
                meaning = response_text.strip() if isinstance(response_text, str) else str(response_text).strip()
                if not meaning or len(meaning) < 2:
                    # Fallback to column name if response is too short
                    meaning = f"Column: {column_name}"
                
                return meaning
                
            except Exception as agent_error:
                self.logger.warning(f"⚠️ Agent-based semantic meaning inference failed for {column_name}: {agent_error}, using column name")
                return f"Column: {column_name}"
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to infer semantic meaning via agent for {column_name}: {e}, using column name")
            return f"Column: {column_name}"
    
    async def create_representative_embeddings(
        self,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        sampling_strategy: str = "every_nth",
        n: int = 10,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create representative embeddings from parsed content.
        
        Flow:
        1. Retrieve parsed file from Content Steward (parquet)
        2. Read parquet file (pandas)
        3. Extract metadata (data types, column names, etc.)
        4. Sample representative rows (every 10th row)
        5. Create embeddings for each column (metadata, meaning, samples)
        6. Extract enhanced metadata (data_type, semantic_meaning, sample_values, etc.)
        7. Store via SemanticDataAbstraction
        
        Args:
            parsed_file_id: Parsed file identifier (parquet in GCS)
            content_metadata: Content metadata from parsing
            sampling_strategy: Sampling strategy ("every_nth")
            n: Sample every nth row (default: 10)
            user_context: Optional user context
        
        Returns:
            Dict with success status, embeddings list, and counts
        """
        # Initialize variables at function scope (before try block)
        df = None
        unstructured_chunks = None
        format_type = None
        content_type = None
        
        try:
            self.logger.info(f"📊 Creating embeddings from parsed file: {parsed_file_id}")
            
            # Check parsing type from content_metadata
            parsing_type = content_metadata.get("parsing_type", "structured")
            
            # ⭐ NEW: Handle workflow and SOP parsing types differently
            if parsing_type in ["workflow", "sop"]:
                return await self._create_workflow_sop_embeddings(
                    parsed_file_id=parsed_file_id,
                    content_metadata=content_metadata,
                    parsing_type=parsing_type,
                    user_context=user_context
                )
            
            # Step 1: Retrieve parsed parquet file from Data Steward (PRIMARY PATHWAY - REQUIRED)
            # Note: Content Steward consolidated into Data Steward
            if not self.service.data_steward:
                raise ValueError("Data Steward not available - cannot retrieve parsed file. This is required for embedding creation.")
            
            try:
                # ✅ Use get_parsed_file() which looks up metadata and retrieves the actual GCS file
                # ✅ CLARIFIED: parsed_file_id IS the GCS file UUID (stored in parsed_data_files.parsed_file_id)
                # The parsed file is stored in GCS with this UUID, and metadata is stored in parsed_data_files table
                # This UUID is returned from store_parsed_file() and used consistently throughout the platform
                parsed_file_result = await self.service.data_steward.get_parsed_file(parsed_file_id)
                if not parsed_file_result:
                    raise ValueError(f"Parsed file not found: {parsed_file_id}. File must be parsed and saved before embeddings can be created.")
                
                # get_parsed_file() returns: {parsed_file_id, metadata, file_data, format_type, content_type}
                self.logger.info(f"🔍 [create_representative_embeddings] parsed_file_result keys: {list(parsed_file_result.keys())}")
                file_content = parsed_file_result.get("file_data")
                format_type = parsed_file_result.get("format_type", "parquet").lower()
                content_type = parsed_file_result.get("content_type") or content_metadata.get("content_type", "structured")
                self.logger.info(f"🔍 [create_representative_embeddings] file_data type: {type(file_content)}, length: {len(file_content) if isinstance(file_content, bytes) else 'N/A'}, format_type: {format_type}, content_type: {content_type}")
                
                if not file_content:
                    available_fields = list(parsed_file_result.keys()) if parsed_file_result else []
                    self.logger.error(f"❌ Parsed file has no content: {parsed_file_id}. Available fields: {available_fields}")
                    raise ValueError(f"Parsed file has no content: {parsed_file_id}. Available fields: {available_fields}. File must be parsed and saved before embeddings can be created.")
                
                # Support all format types: parquet, jsonl, json_structured, json_chunks
                
                if format_type == "parquet" or format_type == "parquet_file":
                    # Validate parquet magic bytes before reading
                    if isinstance(file_content, bytes) and len(file_content) >= 4:
                        magic_bytes = file_content[:4]
                        if magic_bytes != b'PAR1':
                            self.logger.error(f"❌ Invalid parquet magic bytes: {magic_bytes} (expected PAR1)")
                            self.logger.error(f"   Content type: {type(file_content)}, length: {len(file_content)}")
                            self.logger.error(f"   First 20 bytes: {file_content[:20]}")
                            self.logger.error(f"   Last 20 bytes: {file_content[-20:]}")
                            raise ValueError(f"Retrieved file is not a valid parquet file: magic_bytes={magic_bytes}, expected PAR1")
                        self.logger.info(f"✅ Parquet magic bytes validated: {magic_bytes}, size: {len(file_content)} bytes")
                    else:
                        self.logger.error(f"❌ Invalid parquet content: type={type(file_content)}, length={len(file_content) if isinstance(file_content, bytes) else 'N/A'}")
                        raise ValueError(f"Retrieved file content is not valid bytes: type={type(file_content)}")
                
                    # Read parquet from bytes
                    parquet_buffer = io.BytesIO(file_content)
                    df = pd.read_parquet(parquet_buffer)
                    self.logger.info(f"✅ Loaded parquet file: {len(df)} rows, {len(df.columns)} columns")
                    
                elif format_type == "jsonl":
                    # JSONL format: one JSON object per line (structured data)
                    if isinstance(file_content, bytes):
                        file_content = file_content.decode('utf-8')
                    
                    lines = file_content.strip().split('\n')
                    records = []
                    for line in lines:
                        if line.strip():
                            try:
                                records.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                self.logger.warning(f"⚠️ Skipping invalid JSON line: {e}")
                                continue
                    
                    if not records:
                        raise ValueError(f"Parsed file contains no valid JSON records: {parsed_file_id}")
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(records)
                    self.logger.info(f"✅ Loaded JSONL file: {len(df)} rows, {len(df.columns)} columns")
                    
                elif format_type == "json_structured":
                    # JSON Structured format: single JSON object or array (structured data)
                    if isinstance(file_content, bytes):
                        file_content = file_content.decode('utf-8')
                    
                    data = json.loads(file_content)
                    if isinstance(data, list):
                        # Array of objects
                        df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        # Single object - convert to DataFrame with one row
                        df = pd.DataFrame([data])
                    else:
                        raise ValueError(f"json_structured format must be a JSON object or array, got: {type(data)}")
                    
                    self.logger.info(f"✅ Loaded JSON structured file: {len(df)} rows, {len(df.columns)} columns")
                    
                elif format_type == "json_chunks":
                    # JSON Chunks format: array of text chunks (unstructured data)
                    if isinstance(file_content, bytes):
                        file_content = file_content.decode('utf-8')
                    
                    chunks = json.loads(file_content)
                    if not isinstance(chunks, list):
                        raise ValueError(f"json_chunks format must be a JSON array, got: {type(chunks)}")
                    
                    # Extract text from chunks (chunks can be strings or objects with 'text' field)
                    unstructured_chunks = []
                    for chunk in chunks:
                        if isinstance(chunk, dict):
                            text = chunk.get("text", "")
                            if text:
                                unstructured_chunks.append({"text": text, "metadata": chunk.get("metadata", {})})
                        elif isinstance(chunk, str):
                            unstructured_chunks.append({"text": chunk, "metadata": {}})
                    
                    if not unstructured_chunks:
                        raise ValueError(f"Parsed file contains no valid text chunks: {parsed_file_id}")
                    
                    self.logger.info(f"✅ Loaded JSON chunks file: {len(unstructured_chunks)} chunks (unstructured content)")
                    # Note: unstructured_chunks will be processed differently (not as DataFrame)
                    
                else:
                    raise ValueError(f"Unsupported format type: {format_type}. Supported formats: parquet, jsonl, json_structured, json_chunks")
                
                # Validate data is not empty
                if df is not None and len(df) == 0:
                    raise ValueError(f"Parsed file is empty: {parsed_file_id}. Cannot create embeddings from empty data.")
                if unstructured_chunks is not None and len(unstructured_chunks) == 0:
                    raise ValueError(f"Parsed file contains no valid chunks: {parsed_file_id}. Cannot create embeddings from empty data.")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to retrieve parsed file: {e}")
                raise  # Fail fast - no fallbacks
            
            # Ensure content_type and format_type are set (fallback if not set in try block)
            if content_type is None:
                content_type = content_metadata.get("content_type", "structured")
                self.logger.warning(f"⚠️ content_type not set from parsed_file_result, using fallback: {content_type}")
            if format_type is None:
                format_type = "parquet"
                self.logger.warning(f"⚠️ format_type not set from parsed_file_result, using fallback: {format_type}")
            
            # Step 3: Route to appropriate embedding creation strategy based on content type
            embeddings = []
            content_id = content_metadata.get("content_id") or content_metadata.get("metadata_id")
            file_id = content_metadata.get("file_id")
            
            if not content_id:
                # Generate content_id if not present
                import uuid
                content_id = f"content_{uuid.uuid4().hex[:16]}"
                self.logger.warning(f"⚠️ content_id not in metadata, generated: {content_id}")
            
            # Check if this is part of a hybrid file (has correlation metadata)
            correlation_metadata = content_metadata.get("correlation_metadata", {})
            is_hybrid_part = correlation_metadata.get("is_hybrid_part", False)
            hybrid_file_id = correlation_metadata.get("hybrid_file_id")
            hybrid_part_type = correlation_metadata.get("part_type")  # "structured" or "unstructured"
            
            # Route based on content type and format
            if unstructured_chunks is not None:
                # Unstructured content: Create document-based embeddings for chunks
                self.logger.info(f"📄 Creating document-based embeddings for {len(unstructured_chunks)} chunks")
                embeddings = await self._create_document_embeddings(
                    unstructured_chunks=unstructured_chunks,
                    content_id=content_id,
                    file_id=file_id,
                    content_metadata=content_metadata,
                    sampling_strategy=sampling_strategy,
                    n=n,
                    is_hybrid_part=is_hybrid_part,
                    hybrid_file_id=hybrid_file_id,
                    hybrid_part_type=hybrid_part_type
                )
            elif format_type in ["json_structured"] and content_type == "workflow":
                # Workflow content: Create structure-based embeddings
                self.logger.info(f"🔄 Creating workflow structure-based embeddings")
                embeddings = await self._create_workflow_embeddings(
                    df=df,
                    content_id=content_id,
                    file_id=file_id,
                    content_metadata=content_metadata
                )
            else:
                # Structured content: Create column-based embeddings (existing logic)
                self.logger.info(f"📊 Creating column-based embeddings for structured data")
                # Extract metadata from content_metadata (preferred) or DataFrame
                metadata = content_metadata.get("metadata", {})
                columns = metadata.get("columns", [])
                if not columns:
                    # Fallback: extract from DataFrame
                    columns = [{"name": col, "data_type": str(df[col].dtype)} for col in df.columns]
                
                # Sample representative rows (every 10th row)
                if sampling_strategy == "every_nth":
                    sampled_df = df.iloc[::n]  # Every nth row
                else:
                    sampled_df = df  # No sampling
                self.logger.info(f"📊 Sampled {len(sampled_df)} rows (strategy: {sampling_strategy}, n: {n})")
                
                # Create embeddings for each column with enhanced metadata
                for col_idx, column_info in enumerate(columns):
                    column_name = column_info.get("name") if isinstance(column_info, dict) else str(column_info)
                    
                    # Get data type from metadata or DataFrame
                    if isinstance(column_info, dict):
                        data_type = column_info.get("data_type") or column_info.get("type") or "string"
                    else:
                        data_type = "string"
                    
                    # Extract column data from sampled DataFrame
                    sample_values = []
                    if column_name in sampled_df.columns:
                        column_data = sampled_df[column_name]
                        data_type = str(sampled_df[column_name].dtype) if data_type == "string" else data_type
                        
                        # Get sample values (first 10 non-null values as text)
                        for val in column_data.dropna().head(10):
                            # Convert to string (handles numpy types)
                            try:
                                if pd.isna(val):
                                    continue
                                # Convert numpy types to native Python types
                                if isinstance(val, (np.integer, np.int64, np.int32)):
                                    sample_values.append(str(int(val)))
                                elif isinstance(val, (np.floating, np.float64, np.float32)):
                                    sample_values.append(str(float(val)))
                                elif isinstance(val, np.bool_):
                                    sample_values.append(str(bool(val)))
                                else:
                                    sample_values.append(str(val))
                            except Exception:
                                sample_values.append(str(val))
                    else:
                        self.logger.warning(f"⚠️ Column {column_name} not found in sampled DataFrame - this should not happen")
                    
                    # Create embedding text for each type
                    # Metadata embedding: column name + data type + structure
                    metadata_text = f"Column: {column_name}, Type: {data_type}, Position: {col_idx}"
                    
                    # Meaning embedding: semantic meaning (inferred via LLM)
                    meaning_text = await self._infer_semantic_meaning(column_name, data_type, sample_values)
                    
                    # Samples embedding: representative sample values
                    samples_text = f"Sample values: {', '.join(sample_values[:5])}"  # First 5 samples
                    
                    # Generate embeddings using HuggingFaceAdapter (PRIMARY PATHWAY ONLY - NO FALLBACKS)
                    if not self.service.hf_adapter:
                        raise ValueError("HuggingFaceAdapter not available - embeddings cannot be generated. Ensure HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL and HUGGINGFACE_EMBEDDINGS_API_KEY are configured.")
                    
                    try:
                        metadata_result = await self.service.hf_adapter.generate_embedding(metadata_text)
                        meaning_result = await self.service.hf_adapter.generate_embedding(meaning_text)
                        samples_result = await self.service.hf_adapter.generate_embedding(samples_text)
                        
                        metadata_embedding = metadata_result.get("embedding", [])
                        meaning_embedding = meaning_result.get("embedding", [])
                        samples_embedding = samples_result.get("embedding", [])
                        
                        if not metadata_embedding or not meaning_embedding or not samples_embedding:
                            raise ValueError(f"Failed to generate embeddings for column {column_name} - HuggingFaceAdapter returned empty results")
                        
                        self.logger.debug(f"✅ Generated embeddings via HuggingFaceAdapter for column: {column_name}")
                    except Exception as e:
                        self.logger.error(f"❌ HuggingFaceAdapter failed for {column_name}: {e}")
                        raise  # Fail fast - no fallbacks
                    
                    # Build embedding document with enhanced metadata
                    embedding_doc = {
                        "column_name": column_name,
                        # Embeddings (vectors)
                        "metadata_embedding": metadata_embedding,
                        "meaning_embedding": meaning_embedding,
                        "samples_embedding": samples_embedding,
                        # Enhanced metadata (text - for preview reconstruction)
                        "data_type": data_type,  # ✅ NEW: Store data type
                        "semantic_meaning": meaning_text,  # ✅ NEW: Store meaning as text
                        "sample_values": sample_values,  # ✅ NEW: Store samples as text array
                        "row_count": len(df),  # ✅ NEW: Store row count
                        "column_position": col_idx,  # ✅ NEW: Store column order
                        "semantic_id": None,  # Will be populated by semantic matching (future)
                        "semantic_model_recommendation": None,  # ✅ NEW: Will be populated by semantic matching (future)
                        # Correlation metadata for hybrid files
                        "content_type": content_type,
                        "format_type": format_type,
                        "is_hybrid_part": is_hybrid_part,
                        "hybrid_file_id": hybrid_file_id,
                        "hybrid_part_type": hybrid_part_type
                    }
                    
                    embeddings.append(embedding_doc)
                column_name = column_info.get("name") if isinstance(column_info, dict) else str(column_info)
                
                # Get data type from metadata or DataFrame
                if isinstance(column_info, dict):
                    data_type = column_info.get("data_type") or column_info.get("type") or "string"
                else:
                    data_type = "string"
                
                # Extract column data from sampled DataFrame
                sample_values = []
                if column_name in sampled_df.columns:
                    column_data = sampled_df[column_name]
                    data_type = str(sampled_df[column_name].dtype) if data_type == "string" else data_type
                    
                    # Get sample values (first 10 non-null values as text)
                    for val in column_data.dropna().head(10):
                        # Convert to string (handles numpy types)
                        try:
                            if pd.isna(val):
                                continue
                            # Convert numpy types to native Python types
                            if isinstance(val, (np.integer, np.int64, np.int32)):
                                sample_values.append(str(int(val)))
                            elif isinstance(val, (np.floating, np.float64, np.float32)):
                                sample_values.append(str(float(val)))
                            elif isinstance(val, np.bool_):
                                sample_values.append(str(bool(val)))
                            else:
                                sample_values.append(str(val))
                        except Exception:
                            sample_values.append(str(val))
                else:
                    self.logger.warning(f"⚠️ Column {column_name} not found in sampled DataFrame - this should not happen")
                
                # Create embedding text for each type
                # Metadata embedding: column name + data type + structure
                metadata_text = f"Column: {column_name}, Type: {data_type}, Position: {col_idx}"
                
                # Meaning embedding: semantic meaning (inferred via LLM)
                meaning_text = await self._infer_semantic_meaning(column_name, data_type, sample_values)
                
                # Samples embedding: representative sample values
                samples_text = f"Sample values: {', '.join(sample_values[:5])}"  # First 5 samples
                
                # Generate embeddings using HuggingFaceAdapter (PRIMARY PATHWAY ONLY - NO FALLBACKS)
                if not self.service.hf_adapter:
                    raise ValueError("HuggingFaceAdapter not available - embeddings cannot be generated. Ensure HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL and HUGGINGFACE_EMBEDDINGS_API_KEY are configured.")
                
                try:
                    metadata_result = await self.service.hf_adapter.generate_embedding(metadata_text)
                    meaning_result = await self.service.hf_adapter.generate_embedding(meaning_text)
                    samples_result = await self.service.hf_adapter.generate_embedding(samples_text)
                    
                    metadata_embedding = metadata_result.get("embedding", [])
                    meaning_embedding = meaning_result.get("embedding", [])
                    samples_embedding = samples_result.get("embedding", [])
                    
                    if not metadata_embedding or not meaning_embedding or not samples_embedding:
                        raise ValueError(f"Failed to generate embeddings for column {column_name} - HuggingFaceAdapter returned empty results")
                    
                    self.logger.debug(f"✅ Generated embeddings via HuggingFaceAdapter for column: {column_name}")
                except Exception as e:
                    self.logger.error(f"❌ HuggingFaceAdapter failed for {column_name}: {e}")
                    raise  # Fail fast - no fallbacks
                
                # Build embedding document with enhanced metadata
                # Get parsed_file_id from content_metadata for linking
                parsed_file_id = content_metadata.get("parsed_file_id")
                
                embedding_doc = {
                    "column_name": column_name,
                    # Embeddings (vectors)
                    "metadata_embedding": metadata_embedding,
                    "meaning_embedding": meaning_embedding,
                    "samples_embedding": samples_embedding,
                    # Enhanced metadata (text - for preview reconstruction)
                    "data_type": data_type,  # ✅ NEW: Store data type
                    "semantic_meaning": meaning_text,  # ✅ NEW: Store meaning as text
                    "sample_values": sample_values,  # ✅ NEW: Store samples as text array
                    "row_count": len(df),  # ✅ NEW: Store row count
                    "column_position": col_idx,  # ✅ NEW: Store column order
                    "semantic_id": None,  # Will be populated by semantic matching (future)
                    "semantic_model_recommendation": None,  # ✅ NEW: Will be populated by semantic matching (future)
                    # Link to parsed file for matching
                    "parsed_file_id": parsed_file_id  # ✅ NEW: Store parsed_file_id for matching
                }
                
                embeddings.append(embedding_doc)
            
            self.logger.info(f"✅ Created {len(embeddings)} embedding documents")
            
            # Step 6.5: Create embedding_file record BEFORE storing embeddings
            embedding_file_id = None
            parsed_file_id = content_metadata.get("parsed_file_id")
            
            if not file_id:
                raise ValueError("file_id is required to create embedding_file record")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required to create embedding_file record")
            
            # Get original file metadata to get ui_name
            original_file_name = None
            try:
                # Get file_management_abstraction via infrastructure mixin
                file_management = self.service.get_file_management_abstraction()
                if file_management:
                    original_file = await file_management.get_file(file_id)
                    if original_file:
                        original_file_name = original_file.get("ui_name") or original_file.get("filename", "Unknown File")
                else:
                    self.logger.warning("⚠️ file_management_abstraction not available - using fallback name")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get original file metadata: {e} - using fallback name")
            
            # Generate UI-friendly name
            if not original_file_name:
                original_file_name = f"file_{file_id[:8]}"
            ui_name = f"Embeddings: {original_file_name}"
            
            # Get user context for tenant_id and user_id
            user_id = user_context.get("user_id") if user_context else None
            tenant_id = user_context.get("tenant_id") if user_context else None
            
            if not user_id:
                # Try to get from original file
                if file_management:
                    try:
                        original_file = await file_management.get_file(file_id)
                        if original_file:
                            user_id = original_file.get("user_id")
                            tenant_id = tenant_id or original_file.get("tenant_id")
                    except Exception:
                        pass
            
            if not user_id:
                raise ValueError("user_id is required to create embedding_file record")
            
            # Determine data classification
            data_classification = "client" if tenant_id else "platform"
            
            # Create embedding_file record
            embedding_file_data = {
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "ui_name": ui_name,
                "content_id": content_id,
                "embeddings_count": len(embeddings),
                "embedding_type": content_type or "structured",
                "data_classification": data_classification,
                "status": "active",
                "processing_status": "completed",
                "created_by": user_context.get("service_name", "embedding_service") if user_context else "embedding_service",
                "metadata": {
                    "format_type": format_type,
                    "content_type": content_type,
                    "sampling_strategy": sampling_strategy,
                    "n": n
                }
            }
            
            try:
                # Get file_management_abstraction to access Supabase adapter
                file_management = self.service.get_file_management_abstraction()
                if not file_management:
                    raise ValueError("file_management_abstraction not available - cannot create embedding_file record")
                
                # Access Supabase adapter via file_management_abstraction
                supabase_adapter = file_management.supabase_adapter
                if not supabase_adapter:
                    raise ValueError("Supabase adapter not available - cannot create embedding_file record")
                
                # Create embedding_file record
                embedding_file_result = await supabase_adapter.create_embedding_file(embedding_file_data)
                embedding_file_id = embedding_file_result.get("uuid")
                
                if not embedding_file_id:
                    raise ValueError("Failed to create embedding_file record - no UUID returned")
                
                self.logger.info(f"✅ Created embedding_file record: {embedding_file_id} (ui_name: {ui_name})")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to create embedding_file record: {e}")
                raise ValueError(f"Failed to create embedding_file record: {e}")
            
            # Step 7: Store via SemanticDataAbstraction (with embedding_file_id)
            if not self.service.semantic_data:
                raise ValueError("SemanticDataAbstraction not available - cannot store embeddings")
            
            # Add embedding_file_id to each embedding document
            for emb in embeddings:
                emb["embedding_file_id"] = embedding_file_id
            
            store_result = await self.service.semantic_data.store_semantic_embeddings(
                content_id=content_id,
                file_id=file_id,
                embeddings=embeddings,
                user_context=user_context
            )
            
            if not store_result.get("success"):
                raise ValueError(f"Failed to store embeddings: {store_result.get('error')}")
            
            self.logger.info(f"✅ Stored {store_result.get('stored_count', 0)} embeddings")
            
            return {
                "success": True,
                "embeddings": embeddings,
                "embeddings_count": len(embeddings),
                "content_id": content_id,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "embedding_file_id": embedding_file_id,  # ✅ NEW: Include embedding_file_id in response
                "stored_count": store_result.get("stored_count", 0)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Embedding creation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "embeddings": [],
                "embeddings_count": 0
            }
    
    async def _create_workflow_sop_embeddings(
        self,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        parsing_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create embeddings for workflow or SOP files.
        
        For workflow files:
        - Creates embeddings for nodes (tasks, gateways, events)
        - Creates embeddings for edges (flows, connections)
        - Creates embeddings for workflow metadata
        
        For SOP files:
        - Creates embeddings for sections (headings + content)
        - Creates embeddings for steps (individual steps)
        - Creates embeddings for roles (responsibilities)
        
        Args:
            parsed_file_id: Parsed file identifier
            content_metadata: Content metadata with structure
            parsing_type: "workflow" or "sop"
            user_context: Optional user context
        
        Returns:
            Dict with success status, embeddings list, and counts
        """
        try:
            self.logger.info(f"📊 Creating {parsing_type} embeddings from structure: {parsed_file_id}")
            
            # Get structure from content_metadata
            structure = content_metadata.get("structure", {})
            if not structure:
                raise ValueError(f"{parsing_type} structure not found in content_metadata")
            
            # Generate content_id if not present
            content_id = content_metadata.get("content_id") or content_metadata.get("metadata_id")
            if not content_id:
                import uuid
                content_id = f"content_{uuid.uuid4().hex[:16]}"
                self.logger.warning(f"⚠️ content_id not in metadata, generated: {content_id}")
            
            file_id = content_metadata.get("file_id")
            embeddings = []
            
            # Generate embeddings using HuggingFaceAdapter
            if not self.service.hf_adapter:
                raise ValueError("HuggingFaceAdapter not available - embeddings cannot be generated")
            
            if parsing_type == "workflow":
                # Create embeddings for workflow nodes
                nodes = structure.get("nodes", [])
                for node in nodes:
                    node_id = node.get("id", "")
                    node_type = node.get("type", "default")
                    node_label = node.get("label", "")
                    node_data = node.get("data", {})
                    
                    # Create embedding text for node
                    node_text = f"Workflow Node: {node_label}, Type: {node_type}, ID: {node_id}"
                    if isinstance(node_data, dict):
                        node_text += f", Data: {str(node_data)}"
                    
                    # Generate embedding
                    node_result = await self.service.hf_adapter.generate_embedding(node_text)
                    node_embedding = node_result.get("embedding", [])
                    
                    if node_embedding:
                        embeddings.append({
                            "type": "workflow_node",
                            "node_id": node_id,
                            "node_type": node_type,
                            "node_label": node_label,
                            "embedding": node_embedding,
                            "data": node_data
                        })
                
                # Create embeddings for workflow edges
                edges = structure.get("edges", [])
                for edge in edges:
                    edge_id = edge.get("id", "")
                    source = edge.get("source", "")
                    target = edge.get("target", "")
                    edge_label = edge.get("label", "")
                    edge_data = edge.get("data", {})
                    
                    # Create embedding text for edge
                    edge_text = f"Workflow Edge: {edge_label}, From: {source}, To: {target}, ID: {edge_id}"
                    if isinstance(edge_data, dict):
                        edge_text += f", Data: {str(edge_data)}"
                    
                    # Generate embedding
                    edge_result = await self.service.hf_adapter.generate_embedding(edge_text)
                    edge_embedding = edge_result.get("embedding", [])
                    
                    if edge_embedding:
                        embeddings.append({
                            "type": "workflow_edge",
                            "edge_id": edge_id,
                            "source": source,
                            "target": target,
                            "edge_label": edge_label,
                            "embedding": edge_embedding,
                            "data": edge_data
                        })
                
                # Create embedding for workflow metadata
                workflow_metadata = structure.get("metadata", {})
                if workflow_metadata:
                    metadata_text = f"Workflow Metadata: {str(workflow_metadata)}"
                    metadata_result = await self.service.hf_adapter.generate_embedding(metadata_text)
                    metadata_embedding = metadata_result.get("embedding", [])
                    
                    if metadata_embedding:
                        embeddings.append({
                            "type": "workflow_metadata",
                            "embedding": metadata_embedding,
                            "metadata": workflow_metadata
                        })
            
            elif parsing_type == "sop":
                # Create embeddings for SOP sections
                sections = structure.get("sections", [])
                for section in sections:
                    section_id = section.get("id", "")
                    section_heading = section.get("heading", "")
                    section_content = section.get("content", "")
                    steps = section.get("steps", [])
                    
                    # Create embedding for section heading + content
                    section_text = f"SOP Section: {section_heading}\nContent: {section_content}"
                    section_result = await self.service.hf_adapter.generate_embedding(section_text)
                    section_embedding = section_result.get("embedding", [])
                    
                    if section_embedding:
                        embeddings.append({
                            "type": "sop_section",
                            "section_id": section_id,
                            "section_heading": section_heading,
                            "section_content": section_content,
                            "embedding": section_embedding,
                            "step_count": len(steps)
                        })
                    
                    # Create embeddings for steps within section
                    for step in steps:
                        step_id = step.get("id", "")
                        step_text_content = step.get("text", "") or step.get("content", "")
                        step_number = step.get("step_number", "")
                        
                        # Create embedding for step
                        step_text = f"SOP Step {step_number}: {step_text_content}"
                        step_result = await self.service.hf_adapter.generate_embedding(step_text)
                        step_embedding = step_result.get("embedding", [])
                        
                        if step_embedding:
                            embeddings.append({
                                "type": "sop_step",
                                "step_id": step_id,
                                "section_id": section_id,
                                "step_number": step_number,
                                "step_text": step_text_content,
                                "embedding": step_embedding
                            })
                
                # Create embeddings for roles
                roles = structure.get("roles", [])
                for role in roles:
                    role_text = f"SOP Role: {role}"
                    role_result = await self.service.hf_adapter.generate_embedding(role_text)
                    role_embedding = role_result.get("embedding", [])
                    
                    if role_embedding:
                        embeddings.append({
                            "type": "sop_role",
                            "role": role,
                            "embedding": role_embedding
                        })
                
                # Create embedding for SOP title
                title = structure.get("title", "")
                if title:
                    title_text = f"SOP Title: {title}"
                    title_result = await self.service.hf_adapter.generate_embedding(title_text)
                    title_embedding = title_result.get("embedding", [])
                    
                    if title_embedding:
                        embeddings.append({
                            "type": "sop_title",
                            "title": title,
                            "embedding": title_embedding
                        })
            
            self.logger.info(f"✅ Created {len(embeddings)} {parsing_type} embeddings")
            
            # Store via SemanticDataAbstraction
            if not self.service.semantic_data:
                raise ValueError("SemanticDataAbstraction not available - cannot store embeddings")
            
            store_result = await self.service.semantic_data.store_semantic_embeddings(
                content_id=content_id,
                file_id=file_id,
                embeddings=embeddings,
                user_context=user_context
            )
            
            if not store_result.get("success"):
                raise ValueError(f"Failed to store embeddings: {store_result.get('error')}")
            
            self.logger.info(f"✅ Stored {store_result.get('stored_count', 0)} {parsing_type} embeddings")
            
            return {
                "success": True,
                "content_id": content_id,
                "embeddings_count": len(embeddings),
                "stored_count": store_result.get("stored_count", len(embeddings)),
                "parsing_type": parsing_type,
                "embeddings": embeddings
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create {parsing_type} embeddings: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "parsing_type": parsing_type,
                "embeddings_count": 0
            }
    
    async def _create_document_embeddings(
        self,
        unstructured_chunks: List[Dict[str, Any]],
        content_id: str,
        file_id: Optional[str],
        content_metadata: Dict[str, Any],
        sampling_strategy: str = "every_nth",
        n: int = 10,
        is_hybrid_part: bool = False,
        hybrid_file_id: Optional[str] = None,
        hybrid_part_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create document-based embeddings for unstructured text chunks.
        
        For unstructured content, we create embeddings for each text chunk,
        not column-based embeddings like structured data.
        
        Args:
            unstructured_chunks: List of chunk dictionaries with 'text' and 'metadata'
            content_id: Content identifier
            file_id: File identifier
            content_metadata: Content metadata
            sampling_strategy: Sampling strategy ("every_nth")
            n: Sample every nth chunk (default: 10)
        
        Returns:
            List of embedding documents
        """
        embeddings = []
        
        # Sample representative chunks (every nth chunk)
        if sampling_strategy == "every_nth":
            sampled_chunks = unstructured_chunks[::n]  # Every nth chunk
        else:
            sampled_chunks = unstructured_chunks  # No sampling
        
        self.logger.info(f"📄 Processing {len(sampled_chunks)} chunks (from {len(unstructured_chunks)} total)")
        
        if not self.service.hf_adapter:
            raise ValueError("HuggingFaceAdapter not available - embeddings cannot be generated")
        
        for chunk_idx, chunk in enumerate(sampled_chunks):
            text = chunk.get("text", "")
            chunk_metadata = chunk.get("metadata", {})
            
            if not text:
                self.logger.warning(f"⚠️ Skipping empty chunk at index {chunk_idx}")
                continue
            
            # Create embedding for chunk text
            try:
                chunk_result = await self.service.hf_adapter.generate_embedding(text)
                chunk_embedding = chunk_result.get("embedding", [])
                
                if not chunk_embedding:
                    self.logger.warning(f"⚠️ Failed to generate embedding for chunk {chunk_idx}")
                    continue
                
                # Build embedding document for chunk
                # Get parsed_file_id from content_metadata for linking
                parsed_file_id = content_metadata.get("parsed_file_id")
                
                embedding_doc = {
                    "chunk_index": chunk_idx,
                    "chunk_text": text,
                    "chunk_embedding": chunk_embedding,
                    "chunk_metadata": chunk_metadata,
                    "total_chunks": len(unstructured_chunks),
                    "content_type": "unstructured",
                    "format_type": "json_chunks",
                    "embedding_type": "document_chunk",
                    # Correlation metadata for hybrid files
                    "is_hybrid_part": is_hybrid_part,
                    "hybrid_file_id": hybrid_file_id,
                    "hybrid_part_type": hybrid_part_type,
                    # Link to parsed file for matching
                    "parsed_file_id": parsed_file_id  # ✅ NEW: Store parsed_file_id for matching
                }
                
                embeddings.append(embedding_doc)
                
            except Exception as e:
                self.logger.error(f"❌ Failed to create embedding for chunk {chunk_idx}: {e}")
                continue
        
        self.logger.info(f"✅ Created {len(embeddings)} document-based embeddings")
        return embeddings
    
    async def _create_workflow_embeddings(
        self,
        df: pd.DataFrame,
        content_id: str,
        file_id: Optional[str],
        content_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create structure-based embeddings for workflow/SOP content.
        
        Workflow files contain nodes, edges, and structure information.
        We create embeddings for workflow elements (nodes, edges, processes).
        
        Args:
            df: DataFrame containing workflow structure (may be empty if structure is in metadata)
            content_id: Content identifier
            file_id: File identifier
            content_metadata: Content metadata (should contain workflow structure)
        
        Returns:
            List of embedding documents
        """
        embeddings = []
        
        # Extract workflow structure from metadata
        metadata = content_metadata.get("metadata", {})
        structure = metadata.get("structure", {}) or content_metadata.get("structure", {})
        
        nodes = structure.get("nodes", [])
        edges = structure.get("edges", [])
        processes = structure.get("processes", [])
        
        if not self.service.hf_adapter:
            raise ValueError("HuggingFaceAdapter not available - embeddings cannot be generated")
        
        # Create embeddings for nodes
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("type", "default")
            node_label = node.get("label", "")
            node_data = node.get("data", {})
            
            # Create embedding text for node
            node_text = f"Workflow node: {node_label}, Type: {node_type}, ID: {node_id}"
            
            try:
                node_result = await self.service.hf_adapter.generate_embedding(node_text)
                node_embedding = node_result.get("embedding", [])
                
                if node_embedding:
                    embedding_doc = {
                        "node_id": node_id,
                        "node_type": node_type,
                        "node_label": node_label,
                        "node_embedding": node_embedding,
                        "node_data": node_data,
                        "content_type": "workflow",
                        "format_type": "json_structured",
                        "embedding_type": "workflow_node"
                    }
                    embeddings.append(embedding_doc)
            except Exception as e:
                self.logger.error(f"❌ Failed to create embedding for node {node_id}: {e}")
                continue
        
        # Create embeddings for edges
        for edge in edges:
            edge_id = edge.get("id", "")
            edge_source = edge.get("source", "")
            edge_target = edge.get("target", "")
            edge_label = edge.get("label", "")
            
            # Create embedding text for edge
            edge_text = f"Workflow edge: {edge_label}, From: {edge_source}, To: {edge_target}"
            
            try:
                edge_result = await self.service.hf_adapter.generate_embedding(edge_text)
                edge_embedding = edge_result.get("embedding", [])
                
                if edge_embedding:
                    embedding_doc = {
                        "edge_id": edge_id,
                        "edge_source": edge_source,
                        "edge_target": edge_target,
                        "edge_label": edge_label,
                        "edge_embedding": edge_embedding,
                        "content_type": "workflow",
                        "format_type": "json_structured",
                        "embedding_type": "workflow_edge"
                    }
                    embeddings.append(embedding_doc)
            except Exception as e:
                self.logger.error(f"❌ Failed to create embedding for edge {edge_id}: {e}")
                continue
        
        self.logger.info(f"✅ Created {len(embeddings)} workflow structure-based embeddings (nodes: {len(nodes)}, edges: {len(edges)})")
        return embeddings

