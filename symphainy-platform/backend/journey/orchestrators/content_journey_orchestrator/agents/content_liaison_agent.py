#!/usr/bin/env python3
"""
Content Liaison Agent

Liaison agent for the Content Pillar Service following Smart City patterns.
Handles user interaction and provides guidance for content management.

WHAT (Business Enablement Role): I provide user guidance for content management
HOW (Smart City Role): I use liaison agent patterns for user interaction
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import UserContext
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase


class ContentLiaisonAgent(BusinessLiaisonAgentBase):
    """
    Content Liaison Agent
    
    Liaison agent that handles user interaction and provides guidance for content management.
    Provides conversational interface for content operations.
    
    Uses full Agentic SDK via Agentic Foundation factory.
    """
    
    def __init__(
        self,
        agent_name: str,
        business_domain: str,
        capabilities: List[str],
        required_roles: List[str],
        agui_schema: Any,
        foundation_services: Any,
        agentic_foundation: Any,
        public_works_foundation: Any,
        mcp_client_manager: Any,
        policy_integration: Any,
        tool_composition: Any,
        agui_formatter: Any,
        curator_foundation: Any = None,
        metadata_foundation: Any = None,
        **kwargs
    ):
        """
        Initialize Content Liaison Agent with full SDK dependencies.
        
        This agent is created via Agentic Foundation factory - all dependencies
        are provided by the factory.
        """
        super().__init__(
            agent_name=agent_name,
            business_domain=business_domain,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            **kwargs
        )
        
        self.service_name = agent_name
        
        # Orchestrator (discovered via Curator)
        self.content_orchestrator = None
        
        # Note: Conversation context is now stored in session via SessionManagerService
        # Local conversation_contexts removed - all persistence via session
    
    async def initialize(self):
        """
        Initialize Content Liaison Agent.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking (using AgentBase utility method)
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.service_name
            })
            
            # Call parent initialize (BusinessLiaisonAgentBase)
            await super().initialize()
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "ContentAnalysisOrchestratorService" in services_dict:
                        service_info = services_dict["ContentAnalysisOrchestratorService"]
                        self.content_orchestrator = service_info.get("service_instance")
                        self.logger.info("✅ Discovered ContentAnalysisOrchestrator")
                except Exception as e:
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "ContentAnalysisOrchestrator"})
                    self.logger.warning(f"⚠️ ContentAnalysisOrchestrator not available: {e}")
            
            self.is_initialized = True
            
            # Record health metric (success)
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.service_name
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.service_name
            })
            
            self.logger.info(f"✅ {self.service_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "initialize", details={"agent_name": self.service_name})
            
            # Record health metric (failure)
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.service_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("initialize_complete", success=False, details={
                "agent_name": self.service_name,
                "error": str(e)
            })
            
            self.is_initialized = False
            return False
    
    async def process_user_query(self, query: str, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Process a natural language query from a user.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            query: User's natural language query
            session_id: Session ID (conversations stored in session)
            user_context: User context for authorization
            
        Returns:
            Response to the user query
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_start", success=True, details={
                "session_id": session_id
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "conversation", "query"):
                        await self.record_health_metric("process_user_query_access_denied", 1.0, {
                            "session_id": session_id
                        })
                        await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to process query")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant_id = getattr(user_context, "tenant_id", None)
                if tenant_id and hasattr(self, "public_works_foundation"):
                    try:
                        tenant_service = self.public_works_foundation.get_tenant_service()
                        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                            await self.record_health_metric("process_user_query_tenant_denied", 1.0, {
                                "session_id": session_id,
                                "tenant_id": tenant_id
                            })
                            await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            # Get Session Manager for conversation persistence
            session_manager = None
            try:
                # Try to get session manager via DI container
                if self.di_container and hasattr(self.di_container, 'curator'):
                    curator = self.di_container.curator
                    session_manager = await curator.get_service("SessionManager")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get Session Manager: {e}")
            
            # Note: Conversation context is now stored in session, not locally
            # We still track some local state for processing, but persistence is in session
            
            # Analyze query intent
            intent = await self._analyze_query_intent(query)
            
            # Create minimal local context for processing (not persisted)
            local_context = {
                "session_id": session_id,
                "user_id": user_context.user_id,
                "message_count": 1,  # Will be tracked in session
                "context": {}
            }
            
            # Process based on intent
            if intent["type"] == "file_upload":
                response = await self._handle_file_upload_query(query, local_context, user_context)
            elif intent["type"] == "document_parsing":
                response = await self._handle_document_parsing_query(query, local_context, user_context)
            elif intent["type"] == "format_conversion":
                response = await self._handle_format_conversion_query(query, local_context, user_context)
            elif intent["type"] == "content_validation":
                response = await self._handle_content_validation_query(query, local_context, user_context)
            elif intent["type"] == "metadata_extraction":
                response = await self._handle_metadata_extraction_query(query, local_context, user_context)
            elif intent["type"] == "general_help":
                response = await self._handle_general_help_query(query, local_context, user_context)
            else:
                response = await self._handle_unknown_query(query, local_context, user_context)
            
            # Update orchestrator context in conversation if session manager available
            orchestrator_context = None
            if self.content_orchestrator:
                # Try to get orchestrator workflow info
                orchestrator_context = {
                    "orchestrator": "ContentAnalysisOrchestrator",
                    "status": "active"  # TODO: Get actual workflow status
                }
            
            # Add assistant response to session conversation if session manager available
            if session_manager:
                await session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type="content_liaison",
                    role="assistant",
                    content=response.get("message", "") if isinstance(response, dict) else str(response),
                    orchestrator_context=orchestrator_context
                )
            
            self.logger.info(f"✅ Processed user query for session {session_id}")
            
            # Record health metric (success)
            await self.record_health_metric("process_user_query_success", 1.0, {
                "session_id": session_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_complete", success=True)
            
            return {
                "success": True,
                "session_id": session_id,  # Return session_id
                "response": response,
                "intent": intent,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "process_user_query", details={
                "session_id": session_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("process_user_query_error", 1.0, {
                "session_id": session_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                "error": str(e)
            })
            
            self.logger.error(f"❌ Failed to process user query: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "response": "I apologize, but I encountered an error processing your query. Please try again.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the intent of a user query."""
        query_lower = query.lower()
        
        # Simple intent analysis - in a real implementation, this would use NLP
        if any(word in query_lower for word in ["upload", "file", "add", "import"]):
            return {"type": "file_upload", "confidence": 0.8}
        elif any(word in query_lower for word in ["parse", "extract", "read", "analyze"]):
            return {"type": "document_parsing", "confidence": 0.8}
        elif any(word in query_lower for word in ["convert", "transform", "change format"]):
            return {"type": "format_conversion", "confidence": 0.8}
        elif any(word in query_lower for word in ["validate", "check", "verify", "quality"]):
            return {"type": "content_validation", "confidence": 0.8}
        elif any(word in query_lower for word in ["metadata", "info", "details", "properties"]):
            return {"type": "metadata_extraction", "confidence": 0.8}
        elif any(word in query_lower for word in ["help", "how", "what", "explain"]):
            return {"type": "general_help", "confidence": 0.6}
        else:
            return {"type": "unknown", "confidence": 0.3}
    
    async def _handle_file_upload_query(self, query: str, conversation_context: Dict[str, Any], 
                                      user_context: UserContext) -> str:
        """Handle queries about file upload."""
        try:
            response = "I can help you with file uploads! Here's what you need to know:\n\n"
            response += "**Supported File Types:**\n"
            response += "• PDF documents\n"
            response += "• Microsoft Word (.docx)\n"
            response += "• Microsoft Excel (.xlsx)\n"
            response += "• CSV files\n"
            response += "• Text files (.txt)\n"
            response += "• JSON files\n"
            response += "• XML files\n"
            response += "• COBOL files\n\n"
            response += "**Upload Process:**\n"
            response += "1. Select your file\n"
            response += "2. Choose the file type\n"
            response += "3. Add any metadata (optional)\n"
            response += "4. Click upload\n\n"
            response += "**File Size Limits:**\n"
            response += "• Maximum file size: 100MB\n"
            response += "• Maximum files per upload: 10\n\n"
            response += "Would you like to upload a file now?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error providing file upload guidance: {str(e)}"
    
    async def _handle_document_parsing_query(self, query: str, conversation_context: Dict[str, Any], 
                                           user_context: UserContext) -> str:
        """Handle queries about document parsing."""
        try:
            response = "I can help you with document parsing! Here's what I can do:\n\n"
            response += "**Parsing Types:**\n"
            response += "• **Text Extraction**: Extract plain text from documents\n"
            response += "• **Structured Data**: Extract tables, lists, and structured content\n"
            response += "• **Metadata Parsing**: Extract document properties and metadata\n"
            response += "• **Content Analysis**: Analyze document content and structure\n\n"
            response += "**Supported Formats:**\n"
            response += "• PDF documents\n"
            response += "• Microsoft Office documents\n"
            response += "• CSV and Excel files\n"
            response += "• JSON and XML files\n"
            response += "• COBOL files\n\n"
            response += "**Parsing Process:**\n"
            response += "1. Upload your document\n"
            response += "2. Select parsing type\n"
            response += "3. Configure parsing options\n"
            response += "4. Start parsing\n"
            response += "5. Review results\n\n"
            response += "What type of document would you like to parse?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error providing document parsing guidance: {str(e)}"
    
    async def _handle_format_conversion_query(self, query: str, conversation_context: Dict[str, Any], 
                                            user_context: UserContext) -> str:
        """Handle queries about format conversion."""
        try:
            response = "I can help you convert files between different formats! Here's what's available:\n\n"
            response += "**Conversion Options:**\n"
            response += "• **PDF to DOCX**: Convert PDF to Word document\n"
            response += "• **DOCX to PDF**: Convert Word to PDF\n"
            response += "• **CSV to JSON**: Convert CSV to JSON format\n"
            response += "• **JSON to XML**: Convert JSON to XML\n"
            response += "• **XML to JSON**: Convert XML to JSON\n"
            response += "• **COBOL to CSV**: Convert COBOL to CSV\n\n"
            response += "**Conversion Process:**\n"
            response += "1. Select your source file\n"
            response += "2. Choose target format\n"
            response += "3. Configure conversion options\n"
            response += "4. Start conversion\n"
            response += "5. Download converted file\n\n"
            response += "**Quality Settings:**\n"
            response += "• High quality (slower, better results)\n"
            response += "• Standard quality (balanced)\n"
            response += "• Fast conversion (faster, basic results)\n\n"
            response += "What format would you like to convert to?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error providing format conversion guidance: {str(e)}"
    
    async def _handle_content_validation_query(self, query: str, conversation_context: Dict[str, Any], 
                                             user_context: UserContext) -> str:
        """Handle queries about content validation."""
        try:
            response = "I can help you validate your content! Here's what I can check:\n\n"
            response += "**Validation Types:**\n"
            response += "• **File Integrity**: Check if file is not corrupted\n"
            response += "• **Format Compliance**: Verify file format standards\n"
            response += "• **Content Quality**: Check content for errors and issues\n"
            response += "• **Schema Validation**: Validate against predefined schemas\n"
            response += "• **Business Rules**: Check against business-specific rules\n\n"
            response += "**Validation Rules:**\n"
            response += "• File size limits\n"
            response += "• Required fields\n"
            response += "• Data format requirements\n"
            response += "• Content structure rules\n"
            response += "• Business logic validation\n\n"
            response += "**Validation Process:**\n"
            response += "1. Select file to validate\n"
            response += "2. Choose validation rules\n"
            response += "3. Configure validation options\n"
            response += "4. Run validation\n"
            response += "5. Review validation results\n\n"
            response += "What type of validation would you like to perform?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error providing content validation guidance: {str(e)}"
    
    async def _handle_metadata_extraction_query(self, query: str, conversation_context: Dict[str, Any], 
                                              user_context: UserContext) -> str:
        """Handle queries about metadata extraction."""
        try:
            response = "I can help you extract metadata from your files! Here's what I can extract:\n\n"
            response += "**Metadata Types:**\n"
            response += "• **File Properties**: Name, size, creation date, modification date\n"
            response += "• **Document Metadata**: Author, title, subject, keywords\n"
            response += "• **Technical Metadata**: File format, encoding, compression\n"
            response += "• **Content Metadata**: Word count, page count, language\n"
            response += "• **Custom Metadata**: User-defined properties\n\n"
            response += "**Extraction Process:**\n"
            response += "1. Select file for metadata extraction\n"
            response += "2. Choose metadata fields to extract\n"
            response += "3. Configure extraction options\n"
            response += "4. Start extraction\n"
            response += "5. Review extracted metadata\n\n"
            response += "**Available Fields:**\n"
            response += "• Basic file information\n"
            response += "• Document properties\n"
            response += "• Technical details\n"
            response += "• Content statistics\n"
            response += "• Custom attributes\n\n"
            response += "What metadata would you like to extract?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error providing metadata extraction guidance: {str(e)}"
    
    async def _handle_general_help_query(self, query: str, conversation_context: Dict[str, Any], 
                                       user_context: UserContext) -> str:
        """Handle general help queries."""
        try:
            response = "I'm the Content Liaison Agent! I help you manage and process your content files.\n\n"
            response += "**What I Can Help With:**\n"
            response += "• **File Upload**: Upload and manage your files\n"
            response += "• **Document Parsing**: Extract text and data from documents\n"
            response += "• **Format Conversion**: Convert files between different formats\n"
            response += "• **Content Validation**: Check files for quality and compliance\n"
            response += "• **Metadata Extraction**: Extract information about your files\n\n"
            response += "**Supported File Types:**\n"
            response += "• PDF, DOCX, XLSX, CSV, TXT, JSON, XML, COBOL\n\n"
            response += "**Getting Started:**\n"
            response += "1. Upload your files using the file upload feature\n"
            response += "2. Choose what you want to do with them (parse, convert, validate)\n"
            response += "3. Configure the options for your task\n"
            response += "4. Review the results\n\n"
            response += "What would you like to do with your content?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error providing general help: {str(e)}"
    
    async def _handle_unknown_query(self, query: str, conversation_context: Dict[str, Any], 
                                  user_context: UserContext) -> str:
        """Handle unknown or unclear queries."""
        try:
            response = "I'm not sure I understand your question. Let me help you get started!\n\n"
            response += "**I can help you with:**\n"
            response += "• Uploading and managing files\n"
            response += "• Parsing documents and extracting data\n"
            response += "• Converting files between formats\n"
            response += "• Validating content quality\n"
            response += "• Extracting metadata from files\n\n"
            response += "Could you please rephrase your question or ask about one of these topics?"
            
            return response
            
        except Exception as e:
            return f"I encountered an error processing your query: {str(e)}"
    
    async def provide_guidance(self, topic: str, user_context: UserContext = None) -> Dict[str, Any]:
        """
        Provide guidance or information on a specific content management topic.
        
        Args:
            topic: Topic to provide guidance on
            user_context: User context for authorization
            
        Returns:
            Guidance information
        """
        try:
            topic_lower = topic.lower()
            
            if "upload" in topic_lower or "file" in topic_lower:
                guidance = await self._handle_file_upload_query("", {}, user_context)
            elif "parse" in topic_lower or "document" in topic_lower:
                guidance = await self._handle_document_parsing_query("", {}, user_context)
            elif "convert" in topic_lower or "format" in topic_lower:
                guidance = await self._handle_format_conversion_query("", {}, user_context)
            elif "validate" in topic_lower or "validation" in topic_lower:
                guidance = await self._handle_content_validation_query("", {}, user_context)
            elif "metadata" in topic_lower or "extract" in topic_lower:
                guidance = await self._handle_metadata_extraction_query("", {}, user_context)
            else:
                guidance = await self._handle_general_help_query("", {}, user_context)
            
            return {
                "success": True,
                "topic": topic,
                "guidance": guidance,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to provide guidance for topic {topic}: {e}")
            return {
                "success": False,
                "topic": topic,
                "guidance": f"I encountered an error providing guidance on {topic}",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_status(self, user_context: UserContext = None) -> Dict[str, Any]:
        """
        Get the current status of the liaison agent.
        
        Args:
            user_context: User context for authorization
            
        Returns:
            Agent status information
        """
        try:
            return {
                "agent_name": self.agent_name,
                "status": "active",
                "initialized": self.is_initialized,
                "capabilities": self.capabilities,
                "active_conversations": 0,  # Conversations now stored in session
                "total_queries_processed": 0,  # Messages now tracked in session
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get agent status: {e}")
            return {
                "agent_name": self.agent_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
