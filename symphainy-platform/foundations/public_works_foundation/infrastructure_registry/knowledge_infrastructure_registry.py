#!/usr/bin/env python3
"""
Knowledge Infrastructure Registry - Registry Layer

Central registry for Librarian knowledge infrastructure capabilities.
This is Layer 5 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I expose and manage knowledge infrastructure capabilities
HOW (Infrastructure Implementation): I provide centralized access to all knowledge infrastructure services
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from foundations.public_works_foundation.composition_services.knowledge_infrastructure_composition_service import KnowledgeInfrastructureCompositionService

logger = logging.getLogger(__name__)

class KnowledgeInfrastructureRegistry:
    """
    Knowledge Infrastructure Registry.
    
    Central registry for Librarian knowledge infrastructure capabilities including:
    - Knowledge discovery and search services
    - Knowledge governance and compliance services
    - Cross-service knowledge coordination
    - Infrastructure health and monitoring
    """
    
    def __init__(self, composition_service: KnowledgeInfrastructureCompositionService):
        """Initialize knowledge infrastructure registry."""
        self.composition_service = composition_service
        self.logger = logging.getLogger(__name__)
        
        # Registry capabilities
        self.capabilities = {
            "knowledge_discovery": {
                "search": True,
                "discovery": True,
                "recommendations": True,
                "path_finding": True,
                "clustering": True
            },
            "knowledge_governance": {
                "policy_management": True,
                "metadata_governance": True,
                "compliance_validation": True,
                "semantic_tagging": True,
                "access_control": True
            },
            "knowledge_coordination": {
                "workflow_orchestration": True,
                "cross_service_coordination": True,
                "status_monitoring": True,
                "analytics_tracking": True
            }
        }
        
        # Service endpoints
        self.endpoints = {
            "knowledge_search": [
                "orchestrate_knowledge_search",
                "coordinate_knowledge_workflow"
            ],
            "knowledge_discovery": [
                "orchestrate_knowledge_discovery",
                "coordinate_knowledge_workflow"
            ],
            "governance_management": [
                "orchestrate_governance_policy_management",
                "orchestrate_metadata_governance",
                "coordinate_knowledge_workflow"
            ],
            "infrastructure_monitoring": [
                "get_infrastructure_status",
                "get_service_health"
            ]
        }
        
        self.logger.info("✅ Knowledge Infrastructure Registry initialized")
    
    # ============================================================================
    # KNOWLEDGE DISCOVERY SERVICES
    # ============================================================================
    
    async def search_knowledge(self, 
                              query: str,
                              search_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search knowledge using the complete infrastructure.
        
        Orchestrates hybrid search with governance and semantic enhancement.
        """
        try:
            self.logger.info(f"🔍 Registry: Searching knowledge: {query}")
            
            if not search_context:
                search_context = {
                    "search_mode": "hybrid",
                    "scope": "global",
                    "limit": 20
                }
            
            # Delegate to composition service
            result = await self.composition_service.orchestrate_knowledge_search(
                query, search_context
            )
            
            self.logger.info(f"✅ Registry: Knowledge search completed: {len(result.get('search_results', {}).get('hits', []))} results")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Knowledge search failed: {e}")
            return {
                "search_results": {"hits": [], "totalHits": 0},
                "error": str(e)
            }
    
    async def discover_related_knowledge(self, 
                                       asset_id: str,
                                       discovery_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Discover related knowledge using the complete infrastructure.
        
        Orchestrates knowledge discovery with governance and compliance.
        """
        try:
            self.logger.info(f"🔗 Registry: Discovering related knowledge: {asset_id}")
            
            if not discovery_context:
                discovery_context = {
                    "relationship_types": ["related_to", "similar_to"],
                    "max_depth": 2
                }
            
            # Delegate to composition service
            result = await self.composition_service.orchestrate_knowledge_discovery(
                asset_id, discovery_context
            )
            
            self.logger.info(f"✅ Registry: Knowledge discovery completed: {len(result.get('related_knowledge', []))} related assets")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Knowledge discovery failed: {e}")
            return {
                "related_knowledge": [],
                "knowledge_paths": [],
                "knowledge_clusters": [],
                "error": str(e)
            }
    
    async def get_knowledge_recommendations(self, 
                                          asset_id: str,
                                          recommendation_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get knowledge recommendations using the complete infrastructure.
        
        Orchestrates recommendation generation with governance filtering.
        """
        try:
            self.logger.info(f"💡 Registry: Getting knowledge recommendations: {asset_id}")
            
            if not recommendation_context:
                recommendation_context = {
                    "limit": 10,
                    "similarity_threshold": 0.6
                }
            
            # Use discovery service for recommendations
            discovery_context = {
                "relationship_types": ["recommended_by", "similar_to"],
                "max_depth": 1,
                **recommendation_context
            }
            
            result = await self.composition_service.orchestrate_knowledge_discovery(
                asset_id, discovery_context
            )
            
            # Extract recommendations from related knowledge
            recommendations = result.get('related_knowledge', [])[:recommendation_context.get('limit', 10)]
            
            self.logger.info(f"✅ Registry: Knowledge recommendations completed: {len(recommendations)} recommendations")
            return {
                "recommendations": recommendations,
                "recommendation_metadata": {
                    "asset_id": asset_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "governance_applied": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Knowledge recommendations failed: {e}")
            return {
                "recommendations": [],
                "error": str(e)
            }
    
    # ============================================================================
    # KNOWLEDGE GOVERNANCE SERVICES
    # ============================================================================
    
    async def create_governance_policy(self, 
                                     policy_data: Dict[str, Any],
                                     governance_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create governance policy using the complete infrastructure.
        
        Orchestrates policy creation with application and compliance validation.
        """
        try:
            self.logger.info(f"📋 Registry: Creating governance policy: {policy_data.get('name', 'Unknown')}")
            
            if not governance_context:
                governance_context = {
                    "target_assets": [],
                    "compliance_rules": []
                }
            
            # Delegate to composition service
            result = await self.composition_service.orchestrate_governance_policy_management(
                policy_data, governance_context
            )
            
            self.logger.info(f"✅ Registry: Governance policy created: {result.get('policy_id', 'None')}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Governance policy creation failed: {e}")
            return {
                "policy_id": None,
                "error": str(e)
            }
    
    async def manage_asset_metadata(self, 
                                  asset_id: str,
                                  metadata_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage asset metadata using the complete infrastructure.
        
        Orchestrates metadata governance with semantic tagging and policy enforcement.
        """
        try:
            self.logger.info(f"📊 Registry: Managing asset metadata: {asset_id}")
            
            # Delegate to composition service
            result = await self.composition_service.orchestrate_metadata_governance(
                asset_id, metadata_context
            )
            
            self.logger.info(f"✅ Registry: Asset metadata managed: {asset_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Asset metadata management failed: {e}")
            return {
                "metadata_result": False,
                "tagging_result": False,
                "error": str(e)
            }
    
    async def validate_compliance(self, 
                                asset_id: str,
                                compliance_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate compliance using the complete infrastructure.
        
        Orchestrates compliance validation with governance policies.
        """
        try:
            self.logger.info(f"✅ Registry: Validating compliance: {asset_id}")
            
            # Get asset metadata for compliance checking
            metadata_context = {
                "metadata": {},
                "compliance_rules": compliance_context.get('compliance_rules', []),
                "policies": compliance_context.get('policies', [])
            }
            
            result = await self.composition_service.orchestrate_metadata_governance(
                asset_id, metadata_context
            )
            
            compliance_result = result.get('compliance_validation', {})
            
            self.logger.info(f"✅ Registry: Compliance validation completed: {compliance_result.get('compliant', False)}")
            return {
                "asset_id": asset_id,
                "compliant": compliance_result.get('compliant', False),
                "violations": compliance_result.get('violations', []),
                "validated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Compliance validation failed: {e}")
            return {
                "asset_id": asset_id,
                "compliant": False,
                "error": str(e)
            }
    
    # ============================================================================
    # CROSS-SERVICE COORDINATION
    # ============================================================================
    
    async def coordinate_knowledge_workflow(self, 
                                         workflow_type: str,
                                         workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate knowledge workflow using the complete infrastructure.
        
        Routes workflow requests to appropriate orchestration methods.
        """
        try:
            self.logger.info(f"🔄 Registry: Coordinating knowledge workflow: {workflow_type}")
            
            # Delegate to composition service
            result = await self.composition_service.coordinate_knowledge_workflow(
                workflow_type, workflow_data
            )
            
            self.logger.info(f"✅ Registry: Knowledge workflow coordinated: {workflow_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Knowledge workflow coordination failed: {e}")
            return {
                "orchestrated": False,
                "reason": "coordination_error",
                "error": str(e)
            }
    
    # ============================================================================
    # INFRASTRUCTURE MONITORING
    # ============================================================================
    
    async def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get comprehensive infrastructure status."""
        try:
            self.logger.info("📊 Registry: Getting infrastructure status")
            
            # Get composition service status
            composition_status = await self.composition_service.get_infrastructure_status()
            
            # Registry-specific status
            registry_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "registry_health": "operational",
                "capabilities": self.capabilities,
                "endpoints": self.endpoints,
                "composition_service": composition_status
            }
            
            # Overall status
            overall_status = "operational"
            if composition_status.get('overall_status') != 'operational':
                overall_status = "degraded"
            
            registry_status["overall_status"] = overall_status
            
            self.logger.info(f"✅ Registry: Infrastructure status retrieved: {overall_status}")
            return registry_status
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Failed to get infrastructure status: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def get_service_health(self, service_name: str = None) -> Dict[str, Any]:
        """Get health status for specific service or all services."""
        try:
            self.logger.info(f"🏥 Registry: Getting service health: {service_name or 'all'}")
            
            # Get overall infrastructure status
            infrastructure_status = await self.get_infrastructure_status()
            
            if service_name:
                # Get specific service health
                if service_name == "knowledge_discovery":
                    health = infrastructure_status.get('composition_service', {}).get('knowledge_discovery', {})
                elif service_name == "knowledge_governance":
                    health = infrastructure_status.get('composition_service', {}).get('knowledge_governance', {})
                elif service_name == "knowledge_coordination":
                    health = {
                        "overall_health": infrastructure_status.get('overall_status', 'unknown'),
                        "registry_health": infrastructure_status.get('registry_health', 'unknown')
                    }
                else:
                    health = {"overall_health": "unknown", "error": "service_not_found"}
                
                return {
                    "service_name": service_name,
                    "health": health,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Get all services health
                return {
                    "all_services": {
                        "knowledge_discovery": infrastructure_status.get('composition_service', {}).get('knowledge_discovery', {}),
                        "knowledge_governance": infrastructure_status.get('composition_service', {}).get('knowledge_governance', {}),
                        "knowledge_coordination": {
                            "overall_health": infrastructure_status.get('overall_status', 'unknown'),
                            "registry_health": infrastructure_status.get('registry_health', 'unknown')
                        }
                    },
                    "overall_status": infrastructure_status.get('overall_status', 'unknown'),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Registry: Failed to get service health: {e}")
            return {
                "service_name": service_name or "all",
                "health": {"overall_health": "error"},
                "error": str(e)
            }
    
    # ============================================================================
    # SERVICE DISCOVERY
    # ============================================================================
    
    async def discover_services(self) -> Dict[str, Any]:
        """Discover available knowledge infrastructure services."""
        try:
            self.logger.info("🔍 Registry: Discovering knowledge infrastructure services")
            
            services = {
                "knowledge_discovery": {
                    "name": "Knowledge Discovery Service",
                    "description": "Knowledge search, discovery, and recommendation services",
                    "capabilities": self.capabilities["knowledge_discovery"],
                    "endpoints": self.endpoints["knowledge_search"] + self.endpoints["knowledge_discovery"]
                },
                "knowledge_governance": {
                    "name": "Knowledge Governance Service", 
                    "description": "Policy management, metadata governance, and compliance services",
                    "capabilities": self.capabilities["knowledge_governance"],
                    "endpoints": self.endpoints["governance_management"]
                },
                "knowledge_coordination": {
                    "name": "Knowledge Coordination Service",
                    "description": "Workflow orchestration and cross-service coordination",
                    "capabilities": self.capabilities["knowledge_coordination"],
                    "endpoints": self.endpoints["infrastructure_monitoring"]
                }
            }
            
            self.logger.info("✅ Registry: Knowledge infrastructure services discovered")
            return {
                "services": services,
                "total_services": len(services),
                "discovered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Service discovery failed: {e}")
            return {
                "services": {},
                "error": str(e)
            }
    
    async def get_service_capabilities(self, service_name: str) -> Dict[str, Any]:
        """Get capabilities for a specific service."""
        try:
            self.logger.info(f"🔧 Registry: Getting service capabilities: {service_name}")
            
            if service_name in self.capabilities:
                capabilities = self.capabilities[service_name]
                endpoints = self.endpoints.get(service_name, [])
                
                return {
                    "service_name": service_name,
                    "capabilities": capabilities,
                    "endpoints": endpoints,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": service_name,
                    "capabilities": {},
                    "endpoints": [],
                    "error": "service_not_found"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Registry: Failed to get service capabilities: {e}")
            return {
                "service_name": service_name,
                "capabilities": {},
                "error": str(e)
            }
    
    # ============================================================================
    # REGISTRY MANAGEMENT
    # ============================================================================
    
    async def register_service(self, 
                             service_name: str,
                             service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new service with the registry."""
        try:
            self.logger.info(f"📝 Registry: Registering service: {service_name}")
            
            # Add service to capabilities
            if service_name not in self.capabilities:
                self.capabilities[service_name] = service_data.get('capabilities', {})
                self.endpoints[service_name] = service_data.get('endpoints', [])
                
                self.logger.info(f"✅ Registry: Service registered: {service_name}")
                return {
                    "service_name": service_name,
                    "registered": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": service_name,
                    "registered": False,
                    "reason": "service_already_exists"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Registry: Service registration failed: {e}")
            return {
                "service_name": service_name,
                "registered": False,
                "error": str(e)
            }
    
    async def unregister_service(self, service_name: str) -> Dict[str, Any]:
        """Unregister a service from the registry."""
        try:
            self.logger.info(f"🗑️ Registry: Unregistering service: {service_name}")
            
            if service_name in self.capabilities:
                del self.capabilities[service_name]
                if service_name in self.endpoints:
                    del self.endpoints[service_name]
                
                self.logger.info(f"✅ Registry: Service unregistered: {service_name}")
                return {
                    "service_name": service_name,
                    "unregistered": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": service_name,
                    "unregistered": False,
                    "reason": "service_not_found"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Registry: Service unregistration failed: {e}")
            return {
                "service_name": service_name,
                "unregistered": False,
                "error": str(e)
            }
    
    async def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary."""
        try:
            self.logger.info("📋 Registry: Getting registry summary")
            
            # Get infrastructure status
            infrastructure_status = await self.get_infrastructure_status()
            
            # Get service discovery
            service_discovery = await self.discover_services()
            
            summary = {
                "registry_info": {
                    "total_services": len(self.capabilities),
                    "total_endpoints": sum(len(endpoints) for endpoints in self.endpoints.values()),
                    "overall_status": infrastructure_status.get('overall_status', 'unknown')
                },
                "service_capabilities": self.capabilities,
                "service_endpoints": self.endpoints,
                "infrastructure_status": infrastructure_status,
                "service_discovery": service_discovery,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info("✅ Registry: Registry summary retrieved")
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Registry: Failed to get registry summary: {e}")
            return {
                "registry_info": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            }

