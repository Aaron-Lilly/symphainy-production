"""
SOP Builder Wizard Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from .micro_modules.sop_intent_handler import SOPIntentHandler
from .micro_modules.sop_manager import SOPManager
from .micro_modules.sop_validator import SOPValidator
from .micro_modules.sop_description_parser import SOPDescriptionParser
from typing import Dict, Any, List, Optional
from datetime import datetime


class SOPBuilderWizardTool(BaseMCP):
    """
    SOP Builder Wizard Tool for Operations Pillar.
    Guides users to create SOPs from free-form descriptions via chat.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "sop_builder_wizard_tool"
        self.pillar = "operations"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("SOPBuilderWizardTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("SOPBuilderWizardTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.intent_handler = SOPIntentHandler(self._logger, self._config)
            self.sop_manager = SOPManager(self._logger, self._config)
            self.sop_validator = SOPValidator(self._logger, self._config)
            self.description_parser = SOPDescriptionParser(self._logger, self._config)
            
            self._logger.info("SOPBuilderWizardTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing SOPBuilderWizardTool micro-modules: {e}")
            raise e
    
    async def build_sop(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        draft_sop: Optional[Dict[str, Any]] = None, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build SOP using micro-module architecture.
        
        Args:
            user_input: User input for SOP building
            conversation_history: Conversation history
            draft_sop: Current SOP draft
            session_token: Session token for Smart City integration
            
        Returns:
            Wizard response with updated SOP draft
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "response": "Session validation failed. Please refresh and try again.",
                        "sop": draft_sop,
                        "status": "error",
                        "next_actions": ["refresh_session"],
                        "metadata": {"error": "invalid_session"}
                    }

            # Process user input
            sop = draft_sop.copy() if draft_sop else None

            # Find the last SOP in the conversation history, if any
            if not sop and conversation_history:
                for turn in reversed(conversation_history):
                    if isinstance(turn.get("agent"), dict) and "sop" in turn["agent"]:
                        sop = turn["agent"]["sop"]
                        break

            # Route user intent using intent handler
            user_intent = await self.intent_handler.route_user_intent(user_input)

            # Handle different user intents using appropriate micro-modules
            if user_intent == "review":
                return await self.intent_handler.handle_review_request(sop, session_token)
            elif user_intent == "publish":
                # Validate SOP before publishing
                validation_result = await self.sop_validator.validate_sop_for_publishing(sop)
                return await self.intent_handler.handle_publish_request(sop, session_token, validation_result)
            elif user_intent == "display":
                return await self.intent_handler.handle_display_request(sop)
            elif user_intent == "help":
                return await self.intent_handler.handle_help_request()
            elif user_intent == "reset":
                return await self.intent_handler.handle_reset_request(session_token)
            else:
                # Default: add a step or continue building
                return await self.sop_manager.add_step_to_sop(sop, user_input, session_token)

        except Exception as e:
            self._logger.error(f"Error in SOPBuilderWizardTool.build_sop: {e}")
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "sop": draft_sop,
                "status": "error",
                "next_actions": ["retry", "help"],
                "metadata": {"error": str(e)}
            }
    
    async def description_to_sop(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert description to SOP structure using description parser."""
        try:
            return await self.description_parser.description_to_sop(user_input, session_token)
        except Exception as e:
            self._logger.error(f"Error in SOPBuilderWizardTool.description_to_sop: {e}")
            return {
                "title": "Error Generating SOP",
                "description": "Failed to generate SOP from description",
                "steps": [],
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "metadata": {"error": str(e), "session_token": session_token}
            }
    
    async def get_sop_statistics(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the SOP using validator."""
        return await self.sop_validator.get_sop_statistics(sop)
    
    async def validate_sop_for_publishing(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SOP before publishing using validator."""
        return await self.sop_validator.validate_sop_for_publishing(sop)
    
    async def get_comprehensive_validation_report(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive validation report using validator."""
        return await self.sop_validator.get_comprehensive_validation_report(sop)
    
    async def get_intent_statistics(self, user_inputs: List[str]) -> Dict[str, Any]:
        """Get statistics about user intent patterns using intent handler."""
        return await self.intent_handler.get_intent_statistics(user_inputs)
    
    async def get_intent_guidance(self, user_input: str) -> Dict[str, Any]:
        """Get guidance for user input using intent handler."""
        return await self.intent_handler.get_intent_guidance(user_input)
    
    async def update_sop_title(
        self, 
        sop: Dict[str, Any], 
        new_title: str, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update SOP title using SOP manager."""
        return await self.sop_manager.update_sop_title(sop, new_title, session_token)
    
    async def update_sop_description(
        self, 
        sop: Dict[str, Any], 
        new_description: str, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update SOP description using SOP manager."""
        return await self.sop_manager.update_sop_description(sop, new_description, session_token)
    
    async def update_step_details(
        self, 
        sop: Dict[str, Any], 
        step_number: int, 
        **kwargs
    ) -> Dict[str, Any]:
        """Update step details using SOP manager."""
        return await self.sop_manager.update_step_details(sop, step_number, **kwargs)
    
    async def remove_step_from_sop(
        self, 
        sop: Dict[str, Any], 
        step_number: int, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Remove step from SOP using SOP manager."""
        return await self.sop_manager.remove_step_from_sop(sop, step_number, session_token)
    
    async def reorder_sop_steps(
        self, 
        sop: Dict[str, Any], 
        new_order: List[int], 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reorder SOP steps using SOP manager."""
        return await self.sop_manager.reorder_sop_steps(sop, new_order, session_token)
    
    async def get_sop_structure(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get SOP structure information using SOP manager."""
        return await self.sop_manager.get_sop_structure(sop)
    
    async def get_sop_metadata(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get SOP metadata using SOP manager."""
        return await self.sop_manager.get_sop_metadata(sop)
    
    async def get_parsing_statistics(
        self, 
        description: str, 
        sop: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get parsing statistics using description parser."""
        return await self.description_parser.get_parsing_statistics(description, sop)
    
    async def get_parsing_recommendations(
        self, 
        description: str, 
        sop: Dict[str, Any]
    ) -> List[str]:
        """Get parsing recommendations using description parser."""
        return await self.description_parser.get_parsing_recommendations(description, sop)
    
    async def get_validation_recommendations(
        self, 
        validation_result: Dict[str, Any]
    ) -> List[str]:
        """Get validation recommendations using validator."""
        return await self.sop_validator.get_validation_recommendations(validation_result)
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get information about tool capabilities and supported features."""
        return {
            "supported_intents": await self.intent_handler.get_supported_intents(),
            "intent_patterns": await self.intent_handler.get_intent_patterns(),
            "architecture": "micro-module",
            "modules": [
                "sop_intent_handler",
                "sop_manager",
                "sop_validator",
                "sop_description_parser"
            ],
            "features": [
                "intent_routing",
                "sop_management",
                "validation_engine",
                "description_parsing",
                "quality_assessment",
                "statistics_analytics"
            ]
        }

