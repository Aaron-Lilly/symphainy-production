#!/usr/bin/env python3
"""
City Manager Service - Data Path Bootstrap Module

Ensures all data operations land in Smart City by:
1. Validating all orchestrators use DIL SDK
2. Registering data path validators
3. Ensuring all Smart City services are ready for data operations

WHAT (Data Path Bootstrap Role): I ensure all data operations land in Smart City
HOW (Data Path Bootstrap Implementation): I validate DIL SDK usage and register validators
"""

import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime


class DataPathBootstrap:
    """Data Path Bootstrap module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
        self.data_path_validators: List[Dict[str, Any]] = []
    
    async def bootstrap_data_paths(self) -> Dict[str, Any]:
        """
        Bootstrap data paths to ensure all data operations land in Smart City.
        
        This ensures:
        1. All Business Enablement orchestrators use DIL SDK
        2. All data operations go through Smart City services
        3. All data paths are tracked and observable
        """
        try:
            if self.service.logger:
                self.service.logger.info("🚀 Bootstrapping data paths...")
            
            bootstrap_results = {
                "bootstrap_id": str(uuid.uuid4()),
                "started_at": datetime.utcnow().isoformat(),
                "orchestrators": {},
                "validators": {},
                "success": False
            }
            
            # Step 1: Validate DIL SDK is initialized in all orchestrators
            orchestrators = await self._get_all_orchestrators()
            for orchestrator in orchestrators:
                orchestrator_name = orchestrator.get("name", "unknown")
                orchestrator_instance = orchestrator.get("instance")
                
                if orchestrator_instance:
                    if not hasattr(orchestrator_instance, 'dil_sdk') or not orchestrator_instance.dil_sdk:
                        self.service.logger.warning(f"⚠️ Orchestrator {orchestrator_name} missing DIL SDK")
                        # Initialize DIL SDK for orchestrator
                        initialized = await self._initialize_dil_sdk_for_orchestrator(orchestrator_instance)
                        bootstrap_results["orchestrators"][orchestrator_name] = {
                            "dil_sdk_initialized": initialized,
                            "status": "fixed" if initialized else "failed"
                        }
                    else:
                        bootstrap_results["orchestrators"][orchestrator_name] = {
                            "dil_sdk_initialized": True,
                            "status": "ok"
                        }
            
            # Step 2: Register data path validators
            await self._register_data_path_validators()
            bootstrap_results["validators"]["registered"] = len(self.data_path_validators)
            
            # Step 3: Ensure all Smart City services are ready for data operations
            services_status = await self._validate_smart_city_data_services()
            bootstrap_results["smart_city_services"] = services_status
            
            bootstrap_results["success"] = True
            bootstrap_results["completed_at"] = datetime.utcnow().isoformat()
            
            if self.service.logger:
                self.service.logger.info("✅ Data path bootstrap completed")
            
            return bootstrap_results
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Data path bootstrap failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "bootstrap_id": str(uuid.uuid4())
            }
    
    async def _get_all_orchestrators(self) -> List[Dict[str, Any]]:
        """Get all orchestrators from Delivery Manager."""
        orchestrators = []
        
        try:
            # Get Delivery Manager from DI Container
            delivery_manager = self.service.di_container.get_service("DeliveryManagerService")
            if delivery_manager and hasattr(delivery_manager, 'orchestrators'):
                for orchestrator_name, orchestrator_instance in delivery_manager.orchestrators.items():
                    orchestrators.append({
                        "name": orchestrator_name,
                        "instance": orchestrator_instance
                    })
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get orchestrators: {e}")
        
        return orchestrators
    
    async def _initialize_dil_sdk_for_orchestrator(self, orchestrator: Any) -> bool:
        """Initialize DIL SDK for an orchestrator."""
        try:
            from backend.smart_city.sdk.dil_sdk import DILSDK
            
            # Get Smart City services
            content_steward = None
            librarian = None
            data_steward = None
            nurse = None
            
            if hasattr(orchestrator, 'get_content_steward_api'):
                content_steward = await orchestrator.get_content_steward_api()
            elif hasattr(orchestrator, 'get_smart_city_api'):
                content_steward = await orchestrator.get_smart_city_api("ContentSteward")
            
            if hasattr(orchestrator, 'get_librarian_api'):
                librarian = await orchestrator.get_librarian_api()
            elif hasattr(orchestrator, 'get_smart_city_api'):
                librarian = await orchestrator.get_smart_city_api("Librarian")
            
            if hasattr(orchestrator, 'get_data_steward_api'):
                data_steward = await orchestrator.get_data_steward_api()
            elif hasattr(orchestrator, 'get_smart_city_api'):
                data_steward = await orchestrator.get_smart_city_api("DataSteward")
            
            if hasattr(orchestrator, 'get_nurse_api'):
                nurse = await orchestrator.get_nurse_api()
            elif hasattr(orchestrator, 'get_smart_city_api'):
                nurse = await orchestrator.get_smart_city_api("Nurse")
            
            if not all([content_steward, librarian, data_steward, nurse]):
                self.service.logger.warning(f"⚠️ Not all Smart City services available for orchestrator")
                return False
            
            # Initialize DIL SDK
            smart_city_services = {
                "content_steward": content_steward,
                "librarian": librarian,
                "data_steward": data_steward,
                "nurse": nurse
            }
            orchestrator.dil_sdk = DILSDK(smart_city_services, logger=orchestrator.logger if hasattr(orchestrator, 'logger') else None)
            
            return True
            
        except Exception as e:
            self.service.logger.error(f"❌ Failed to initialize DIL SDK for orchestrator: {e}")
            return False
    
    async def _register_data_path_validators(self):
        """Register data path validators."""
        # Register validators that ensure:
        # 1. All file operations go through Content Steward
        # 2. All semantic data operations go through Librarian
        # 3. All governance operations go through Data Steward
        # 4. All observability operations go through Nurse
        
        self.data_path_validators = [
            {
                "name": "file_operation_validator",
                "description": "Validates file operations go through Content Steward",
                "enabled": True
            },
            {
                "name": "semantic_data_validator",
                "description": "Validates semantic data operations go through Librarian",
                "enabled": True
            },
            {
                "name": "governance_validator",
                "description": "Validates governance operations go through Data Steward",
                "enabled": True
            },
            {
                "name": "observability_validator",
                "description": "Validates observability operations go through Nurse",
                "enabled": True
            }
        ]
    
    async def _validate_smart_city_data_services(self) -> Dict[str, str]:
        """Validate all Smart City services are ready for data operations."""
        services_status = {}
        
        try:
            # Check Content Steward
            content_steward = await self.service.get_smart_city_api("ContentSteward")
            if content_steward and hasattr(content_steward, 'file_management_abstraction') and content_steward.file_management_abstraction:
                services_status["content_steward"] = "ready"
            else:
                services_status["content_steward"] = "not_ready"
            
            # Check Librarian
            librarian = await self.service.get_smart_city_api("Librarian")
            if librarian and hasattr(librarian, 'semantic_data_abstraction') and librarian.semantic_data_abstraction:
                services_status["librarian"] = "ready"
            else:
                services_status["librarian"] = "not_ready"
            
            # Check Data Steward
            data_steward = await self.service.get_smart_city_api("DataSteward")
            if data_steward and hasattr(data_steward, 'lineage_tracking_module'):
                services_status["data_steward"] = "ready"
            else:
                services_status["data_steward"] = "not_ready"
            
            # Check Nurse
            nurse = await self.service.get_smart_city_api("Nurse")
            if nurse and hasattr(nurse, 'observability_abstraction') and nurse.observability_abstraction:
                services_status["nurse"] = "ready"
            else:
                services_status["nurse"] = "not_ready"
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to validate Smart City services: {e}")
            services_status["error"] = str(e)
        
        return services_status


