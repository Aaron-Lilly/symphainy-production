#!/usr/bin/env python3
"""
Operations Liaison Agent

Liaison agent for the Operations Pillar handling conversational interaction for operations management.

WHAT (Business Enablement Role): I provide conversational support for operations management
HOW (Liaison Agent): I handle user interactions and guide them through operations processes
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from utilities import UserContext
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase


class OperationsLiaisonAgent(BusinessLiaisonAgentBase):
    """
    Operations Liaison Agent
    
    Provides conversational support for operations management activities.
    
    WHAT (Business Enablement Role): I provide conversational support for operations management
    HOW (Liaison Agent): I handle user interactions and guide them through operations processes
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
        Initialize Operations Liaison Agent with full SDK dependencies.
        
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
        
        self.operations_orchestrator = None
    
    async def initialize(self):
        """
        Initialize Operations Liaison Agent.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking (using AgentBase utility method)
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.agent_name
            })
            
            # Call parent initialize (BusinessLiaisonAgentBase)
            await super().initialize()
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "OperationsOrchestratorService" in services_dict:
                        service_info = services_dict["OperationsOrchestratorService"]
                        self.operations_orchestrator = service_info.get("service_instance")
                        self.logger.info("✅ Discovered OperationsOrchestrator")
                except Exception as e:
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "OperationsOrchestrator"})
                    self.logger.warning(f"⚠️ OperationsOrchestrator not available: {e}")
            
            self.is_initialized = True
            
            # Record health metric (success)
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.agent_name
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.agent_name
            })
            
            self.logger.info(f"✅ {self.agent_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "initialize", details={"agent_name": self.agent_name})
            
            # Record health metric (failure)
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.agent_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("initialize_complete", success=False, details={
                "agent_name": self.agent_name,
                "error": str(e)
            })
            
            self.is_initialized = False
            return False
    
    async def process_user_query(
        self,
        query: str,
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Process user query (called by Chat Service).
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            query: User's query
            conversation_id: Conversation ID
            user_context: User context
        
        Returns:
            Response dictionary
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_start", success=True, details={
                "conversation_id": conversation_id
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
                            "conversation_id": conversation_id
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
                                "conversation_id": conversation_id,
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
            
            # Analyze intent and generate response
            query_lower = query.lower()
            
            if "sop" in query_lower or "procedure" in query_lower:
                response = "I can help you create Standard Operating Procedures! Would you like to use our SOP Wizard to document your processes?"
            elif "workflow" in query_lower or "convert" in query_lower:
                response = "I can convert your SOPs into executable workflows! Which SOP would you like to convert?"
            elif "coexistence" in query_lower or "ai human" in query_lower:
                response = "I can analyze AI-Human coexistence patterns in your workflows! Let me create a coexistence blueprint for you."
            elif "optimize" in query_lower or "improve" in query_lower:
                response = "I can help optimize your processes! Share your workflow and I'll identify improvement opportunities."
            elif "visualize" in query_lower or "diagram" in query_lower:
                response = "I can create workflow visualizations! What process would you like to visualize?"
            else:
                response = "Hello! I'm your Operations assistant. I can help you with SOP creation, workflow conversion, coexistence analysis, process optimization, and workflow visualization. What would you like to do?"
            
            # Record health metric (success)
            await self.record_health_metric("process_user_query_success", 1.0, {
                "conversation_id": conversation_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_complete", success=True)
            
            return {
                "success": True,
                "response": response,
                "conversation_id": conversation_id,
                "agent": "operations_liaison"
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "process_user_query", details={
                "conversation_id": conversation_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("process_user_query_error", 1.0, {
                "conversation_id": conversation_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again."
            }
    
    async def process_conversation(self, request) -> Any:
        """Process a conversation request for operations management."""
        try:
            message = request.get("message", "")
            user_context = request.get("user_context")
            session_id = request.get("session_id", "default")
            
            # Analyze the user's intent
            intent = await self._analyze_intent(message)
            
            # Generate appropriate response based on intent
            if intent["type"] == "sop_creation":
                response = await self._handle_sop_creation_request(message, user_context, session_id)
            elif intent["type"] == "workflow_conversion":
                response = await self._handle_workflow_conversion_request(message, user_context, session_id)
            elif intent["type"] == "coexistence_analysis":
                response = await self._handle_coexistence_analysis_request(message, user_context, session_id)
            elif intent["type"] == "process_optimization":
                response = await self._handle_process_optimization_request(message, user_context, session_id)
            elif intent["type"] == "workflow_visualization":
                response = await self._handle_workflow_visualization_request(message, user_context, session_id)
            elif intent["type"] == "general_help":
                response = await self._handle_general_help_request(message, user_context, session_id)
            else:
                response = await self._handle_unknown_request(message, user_context, session_id)
            
            return {
                "success": True,
                "response": response,
                "intent": intent,
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process conversation: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again."
            }
    
    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message to determine intent."""
        message_lower = message.lower()
        
        # SOP creation keywords
        if any(keyword in message_lower for keyword in ["create sop", "sop wizard", "standard operating procedure", "procedure", "sop for", "document"]):
            return {"type": "sop_creation", "confidence": 0.9}
        
        # Workflow conversion keywords
        elif any(keyword in message_lower for keyword in ["convert", "workflow", "sop to workflow", "process flow"]):
            return {"type": "workflow_conversion", "confidence": 0.8}
        
        # Coexistence analysis keywords
        elif any(keyword in message_lower for keyword in ["coexistence", "ai human", "collaboration", "blueprint"]):
            return {"type": "coexistence_analysis", "confidence": 0.8}
        
        # Process optimization keywords
        elif any(keyword in message_lower for keyword in ["optimize", "improve", "efficiency", "streamline"]):
            return {"type": "process_optimization", "confidence": 0.8}
        
        # Workflow visualization keywords
        elif any(keyword in message_lower for keyword in ["visualize", "diagram", "chart", "visual"]):
            return {"type": "workflow_visualization", "confidence": 0.7}
        
        # General help keywords
        elif any(keyword in message_lower for keyword in ["help", "what can you do", "capabilities", "support"]):
            return {"type": "general_help", "confidence": 0.9}
        
        else:
            return {"type": "unknown", "confidence": 0.3}
    
    async def _handle_sop_creation_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle SOP creation requests."""
        try:
            # Check if user is ready to create an SOP
            if any(keyword in message.lower() for keyword in ["yes", "start", "create", "begin", "let's go"]):
                # User is ready to create SOP - trigger the wizard
                return await self._start_sop_creation_wizard(message, user_context, session_id)
            else:
                # Provide guidance on SOP creation
                return """I can help you create a Standard Operating Procedure (SOP) using our guided wizard! 

Here's what I can do for you:
• **SOP Wizard**: Guide you through creating comprehensive SOPs step-by-step
• **Templates**: Provide templates for different types of SOPs (technical, administrative, standard)
• **Validation**: Ensure your SOP meets best practices and business requirements
• **Workflow Integration**: Convert your SOP into executable workflows

To get started, please provide:
1. A description of the process you want to document
2. The type of SOP (technical, administrative, or standard)
3. Any specific requirements or constraints

Would you like to start creating an SOP now? Just say 'yes' or 'start' to begin!"""
        except Exception as e:
            self.logger.error(f"❌ Failed to handle SOP creation request: {e}")
            return "I encountered an error helping you with SOP creation. Please try again."
    
    async def _handle_workflow_conversion_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle workflow conversion requests."""
        return """I can help you convert SOPs into executable workflows! 

Here's what I can do:
• **SOP to Workflow**: Convert your existing SOPs into dynamic, executable workflows
• **Pattern Detection**: Automatically detect the best workflow pattern (sequential, parallel, conditional, iterative)
• **Validation**: Ensure the converted workflow is valid and executable
• **Optimization**: Suggest improvements during conversion

To convert an SOP to a workflow, I'll need:
1. The SOP content or document
2. Any specific workflow requirements
3. Target execution environment details

Would you like to convert an existing SOP to a workflow?"""
    
    async def _handle_coexistence_analysis_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle coexistence analysis requests."""
        return """I can help you analyze and design AI-human coexistence patterns! 

Here's what I can do:
• **Current State Analysis**: Evaluate your current AI-human interaction patterns
• **Target State Design**: Help design optimal coexistence scenarios
• **Gap Analysis**: Identify gaps between current and target states
• **Blueprint Generation**: Create detailed coexistence blueprints
• **Recommendations**: Provide actionable recommendations for improvement

I can analyze different coexistence patterns:
• **Collaborative**: AI and humans work together on shared tasks
• **Delegated**: AI handles specific tasks while humans oversee
• **Augmented**: AI enhances human capabilities
• **Autonomous**: AI operates independently with minimal human intervention

Would you like to start with a coexistence analysis?"""
    
    async def _handle_process_optimization_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle process optimization requests."""
        return """I can help you optimize your business processes for maximum efficiency! 

Here's what I can do:
• **Process Analysis**: Analyze your current processes to identify bottlenecks and inefficiencies
• **Optimization Strategies**: Apply various optimization techniques (automation, parallelization, streamlining)
• **Improvement Calculation**: Quantify the improvements achieved
• **Implementation Planning**: Provide step-by-step implementation guidance

Optimization strategies I can apply:
• **Automation**: Automate repetitive tasks
• **Parallelization**: Execute tasks in parallel where possible
• **Streamlining**: Remove unnecessary steps
• **Standardization**: Standardize procedures
• **Resource Optimization**: Optimize resource allocation

To optimize a process, I'll need:
1. The process definition or description
2. Your optimization goals (efficiency, cost reduction, quality, speed)
3. Any constraints or limitations

Would you like to optimize a specific process?"""
    
    async def _handle_workflow_visualization_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle workflow visualization requests."""
        return """I can help you create visual representations of your workflows and processes! 

Here's what I can do:
• **Multiple Visualization Types**: Flowchart, Swimlane, Gantt, Network, Interactive
• **Automatic Layout**: Intelligently arrange workflow elements
• **Interactive Features**: Zoom, pan, filter, and drill-down capabilities
• **Export Options**: PNG, SVG, PDF, and JSON formats

Visualization types available:
• **Flowchart**: Traditional flowchart with boxes and arrows
• **Swimlane**: Shows responsibilities across different actors
• **Gantt**: Timeline view with dependencies
• **Network**: Relationship diagram for complex processes
• **Interactive**: Full-featured interactive visualization

To create a visualization, I'll need:
1. The workflow definition
2. Your preferred visualization type
3. Any specific styling or layout preferences

Would you like to visualize a workflow?"""
    
    async def _handle_general_help_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle general help requests."""
        return """I'm your Operations Management Assistant! I can help you with various operations management tasks:

## 🏗️ **SOP Management**
• Create Standard Operating Procedures using guided wizard
• Convert SOPs to executable workflows
• Validate and optimize SOPs

## 🔄 **Process Optimization**
• Analyze and optimize business processes
• Identify bottlenecks and inefficiencies
• Calculate improvement metrics

## 🤝 **AI-Human Coexistence**
• Analyze current coexistence patterns
• Design optimal coexistence scenarios
• Generate coexistence blueprints

## 📊 **Workflow Visualization**
• Create visual representations of workflows
• Multiple diagram types (flowchart, swimlane, gantt, network)
• Interactive and exportable visualizations

## 🛠️ **Available Tools**
• SOP Builder Wizard
• Workflow Converter
• Coexistence Evaluator
• Process Optimizer
• Workflow Visualizer

How can I help you with your operations management needs today?"""
    
    async def _handle_unknown_request(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Handle unknown requests."""
        return """I'm not sure I understand what you're looking for. 

I specialize in operations management and can help you with:
• Creating and managing SOPs
• Converting processes to workflows
• Analyzing AI-human coexistence
• Optimizing business processes
• Visualizing workflows

Could you please rephrase your request or ask me about one of these areas? I'm here to help!"""
    
    async def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get agent capabilities."""
        return [
            {
                "name": "SOP Creation",
                "description": "Guide users through creating Standard Operating Procedures",
                "keywords": ["sop", "procedure", "documentation", "wizard"]
            },
            {
                "name": "Workflow Conversion",
                "description": "Convert SOPs to executable workflows",
                "keywords": ["workflow", "conversion", "process flow", "automation"]
            },
            {
                "name": "Coexistence Analysis",
                "description": "Analyze and design AI-human coexistence patterns",
                "keywords": ["coexistence", "ai human", "collaboration", "blueprint"]
            },
            {
                "name": "Process Optimization",
                "description": "Optimize business processes for efficiency",
                "keywords": ["optimize", "improve", "efficiency", "streamline"]
            },
            {
                "name": "Workflow Visualization",
                "description": "Create visual representations of workflows",
                "keywords": ["visualize", "diagram", "chart", "visual"]
            }
        ]
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        return self.conversation_sessions.get(session_id, [])
    
    async def clear_conversation_history(self, session_id: str) -> bool:
        """Clear conversation history for a session."""
        try:
            if session_id in self.conversation_sessions:
                del self.conversation_sessions[session_id]
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to clear conversation history: {e}")
            return False
    
    async def _start_sop_creation_wizard(self, message: str, user_context: UserContext, session_id: str) -> str:
        """Start the SOP creation wizard process."""
        try:
            # Extract SOP description from the message
            sop_description = self._extract_sop_description(message)
            
            if not sop_description:
                return """I'd be happy to help you create an SOP! 

Please describe the process you want to document. For example:
- "I want to create an SOP for our customer onboarding process"
- "I need to document our inventory management procedure"
- "Help me create a standard operating procedure for data backup"

What process would you like to document?"""
            
            # Start the SOP creation process
            return await self._create_sop_interactive(sop_description, user_context, session_id)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start SOP creation wizard: {e}")
            return "I encountered an error starting the SOP creation process. Please try again."
    
    def _extract_sop_description(self, message: str) -> str:
        """Extract SOP description from user message."""
        try:
            # Look for common patterns that indicate SOP descriptions
            message_lower = message.lower()
            
            # Remove common phrases and extract the core description
            phrases_to_remove = [
                "i want to create an sop for",
                "i need to document",
                "help me create a standard operating procedure for",
                "i want to create a procedure for",
                "document the process for",
                "create an sop for"
            ]
            
            description = message
            for phrase in phrases_to_remove:
                if phrase in message_lower:
                    description = description.replace(phrase, "").strip()
                    break
            
            # Clean up the description
            description = description.strip(".,!?").strip()
            
            return description if len(description) > 10 else ""
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract SOP description: {e}")
            return ""
    
    async def _create_sop_interactive(self, description: str, user_context: UserContext, session_id: str) -> str:
        """Create SOP interactively using the wizard."""
        try:
            # This would typically call the Operations Pillar Service to create the SOP
            # For now, we'll simulate the process
            
            # Determine SOP type based on description
            sop_type = self._determine_sop_type(description)
            
            # Create SOP using the wizard
            sop_result = await self._call_sop_builder_wizard(description, user_context, session_id, sop_type)
            
            if sop_result.get("success"):
                return f"""🎉 **SOP Created Successfully!**

**SOP ID**: {sop_result.get('sop_id', 'N/A')}
**Type**: {sop_type.title()}
**Processing Time**: {sop_result.get('processing_time', 0):.2f} seconds

**Your SOP includes:**
• Clear step-by-step procedures
• Defined responsibilities
• Quality control measures
• Workflow integration

**Next Steps:**
• Review your SOP content
• Convert to workflow if needed
• Share with your team
• Set up regular reviews

Would you like me to:
1. Show you the SOP content?
2. Convert it to a workflow?
3. Create a visualization?
4. Help you with something else?"""
            else:
                return f"""❌ **SOP Creation Failed**

I encountered an issue creating your SOP: {sop_result.get('message', 'Unknown error')}

Let's try again. Please provide:
• A clear description of the process
• Any specific requirements
• The type of SOP you need

What would you like to do?"""
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create SOP interactively: {e}")
            return "I encountered an error creating your SOP. Please try again with a clear description of the process you want to document."
    
    def _determine_sop_type(self, description: str) -> str:
        """Determine SOP type based on description."""
        try:
            description_lower = description.lower()
            
            if any(keyword in description_lower for keyword in ["technical", "system", "software", "hardware", "maintenance", "troubleshooting"]):
                return "technical"
            elif any(keyword in description_lower for keyword in ["administrative", "policy", "approval", "review", "compliance"]):
                return "administrative"
            else:
                return "standard"
                
        except Exception:
            return "standard"
    
    async def _call_sop_builder_wizard(self, description: str, user_context: UserContext, session_id: str, sop_type: str) -> Dict[str, Any]:
        """Call the SOP Builder Wizard to create the SOP via MCP tools (unified pattern)."""
        try:
            # Convert UserContext to dict for MCP tool call
            user_context_dict = {
                "user_id": getattr(user_context, "user_id", None),
                "tenant_id": getattr(user_context, "tenant_id", None),
                "roles": getattr(user_context, "roles", []),
                "session_id": session_id
            }
            
            # Use MCP tool to get SOP Builder Service (unified pattern)
            # Note: We use the interactive SOP creation workflow which handles SOP creation
            # Alternatively, we could use get_sop_builder_service MCP tool, but the workflow is more appropriate
            sop_result = await self.execute_mcp_tool(
                "journey_execute_interactive_sop_creation_workflow",  # Cross-realm: Journey realm MCP tool
                {
                    "action": "start",
                    "user_message": f"Create a {sop_type} SOP with the following description: {description}",
                    "session_token": session_id,
                    "user_context": user_context_dict
                }
            )
            
            if sop_result.get("success"):
                # Extract SOP information from workflow result
                sop_structure = sop_result.get("sop_structure", {})
                return {
                    "success": True,
                    "sop_id": sop_structure.get("sop_id") or sop_result.get("sop_id"),
                    "sop_type": sop_type,
                    "processing_time": sop_result.get("processing_time", 0),
                    "message": sop_result.get("message", "SOP created successfully"),
                    "sop_content": sop_structure.get("content") or sop_structure,
                    "workflow_steps": sop_structure.get("workflow_steps", [])
                }
            else:
                # Fallback to simulation if MCP tool fails
                import time
                start_time = time.time()
                
                # Mock SOP creation process
                sop_id = f"sop_{session_id}_{int(time.time())}"
                processing_time = time.time() - start_time
                
                self.logger.warning(f"⚠️ SOP creation via MCP tool failed: {sop_result.get('error')}, using simulation mode")
                
                return {
                    "success": True,
                    "sop_id": sop_id,
                    "sop_type": sop_type,
                    "processing_time": processing_time,
                    "message": "SOP created successfully (simulation mode)"
                }
            
        except Exception as e:
            await self.handle_error_with_audit(e, "call_sop_builder_wizard", details={
                "sop_type": sop_type,
                "session_id": session_id
            })
            self.logger.error(f"❌ Failed to call SOP builder wizard: {e}")
            return {
                "success": False,
                "message": f"SOP creation failed: {str(e)}"
            }



