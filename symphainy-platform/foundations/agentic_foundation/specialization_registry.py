"""
Agent Specialization Registry

Provides configurable and extensible agent specialization management.
Allows dynamic loading and registration of specializations without modifying foundation layers.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin

# Using absolute imports from project root

class SpecializationRegistry(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Registry for managing agent specializations dynamically.
    
    Provides:
    - Dynamic specialization registration
    - Specialization validation and loading
    - Pillar-specific specialization management
    - Extensible specialization system
    """
    
    def __init__(self, config_path: str = None, di_container=None):
        """Initialize specialization registry."""
        if not di_container:
            raise ValueError("DI Container is required for SpecializationRegistry initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.di_container = di_container
        self.service_name = "specialization_registry"
        
        self.config_path = config_path or "agentic/specializations.json"
        self.specializations = {}
        self.pillar_specializations = {}
        
        # Load specializations from config
        self._load_specializations()
        
        self.logger.info("Specialization Registry initialized")
    
    def _load_specializations(self):
        """Load specializations from configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.specializations = config.get("specializations", {})
                    self.pillar_specializations = config.get("pillar_specializations", {})
                self.logger.info(f"Loaded specializations from {self.config_path}")
            else:
                # Create default specializations
                self._create_default_specializations()
                self._save_specializations()
                self.logger.info("Created default specializations")
                
        except Exception as e:
            self.logger.error(f"Failed to load specializations: {e}")
            self._create_default_specializations()
    
    def _create_default_specializations(self):
        """Create default specializations if none exist."""
        self.specializations = {
            "call_center_volumetric_analysis": {
                "name": "Call Center Volumetric Analysis",
                "description": "Expert in analyzing call volume patterns, peak times, and staffing optimization",
                "pillar": "insights",
                "capabilities": ["data_analysis", "pattern_recognition", "optimization"],
                "system_prompt_template": "You are an expert in call center volumetric analysis. You understand peak call volume patterns, seasonal trends, staffing optimization, service level agreements, and customer satisfaction correlation with volume.",
                "keywords": ["call_center", "volume", "staffing", "optimization", "sla"]
            },
            "medical_billing_fraud_detection": {
                "name": "Medical Billing Fraud Detection",
                "description": "Expert in identifying fraudulent billing patterns and compliance issues",
                "pillar": "insights",
                "capabilities": ["fraud_detection", "compliance", "pattern_analysis"],
                "system_prompt_template": "You are an expert in medical billing fraud detection. You understand common fraudulent billing patterns, healthcare compliance requirements (HIPAA, CMS), insurance claim processing, and provider behavior analysis.",
                "keywords": ["medical", "billing", "fraud", "compliance", "healthcare"]
            },
            "retail_customer_behavior": {
                "name": "Retail Customer Behavior Analysis",
                "description": "Expert in customer segmentation, purchase patterns, and retention strategies",
                "pillar": "insights",
                "capabilities": ["customer_analysis", "segmentation", "retention"],
                "system_prompt_template": "You are an expert in retail customer behavior analysis. You understand customer segmentation, purchase pattern analysis, customer lifetime value, seasonal trends, and omnichannel customer journey mapping.",
                "keywords": ["retail", "customer", "behavior", "segmentation", "retention"]
            },
            "financial_risk_assessment": {
                "name": "Financial Risk Assessment",
                "description": "Expert in financial risk analysis, compliance, and regulatory requirements",
                "pillar": "insights",
                "capabilities": ["risk_analysis", "compliance", "financial_modeling"],
                "system_prompt_template": "You are an expert in financial risk assessment. You understand market risk, credit risk, operational risk, regulatory compliance, and financial modeling techniques.",
                "keywords": ["financial", "risk", "compliance", "modeling", "regulatory"]
            },
            "manufacturing_quality_control": {
                "name": "Manufacturing Quality Control",
                "description": "Expert in quality control processes, defect analysis, and process optimization",
                "pillar": "operations",
                "capabilities": ["quality_control", "process_optimization", "defect_analysis"],
                "system_prompt_template": "You are an expert in manufacturing quality control. You understand quality control processes, statistical process control, defect analysis, and manufacturing process optimization.",
                "keywords": ["manufacturing", "quality", "control", "process", "defects"]
            },
            "supply_chain_optimization": {
                "name": "Supply Chain Optimization",
                "description": "Expert in supply chain analysis, logistics optimization, and inventory management",
                "pillar": "operations",
                "capabilities": ["supply_chain", "logistics", "inventory", "optimization"],
                "system_prompt_template": "You are an expert in supply chain optimization. You understand logistics, inventory management, supplier relationships, demand forecasting, and supply chain risk management.",
                "keywords": ["supply_chain", "logistics", "inventory", "optimization", "forecasting"]
            }
        }
        
        # Organize by pillar
        self.pillar_specializations = {
            "insights": ["call_center_volumetric_analysis", "medical_billing_fraud_detection", "retail_customer_behavior", "financial_risk_assessment"],
            "operations": ["manufacturing_quality_control", "supply_chain_optimization"],
            "content": [],
            "experience": []
        }
    
    def _save_specializations(self):
        """Save specializations to configuration file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = {
                "specializations": self.specializations,
                "pillar_specializations": self.pillar_specializations,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Specializations saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save specializations: {e}")
    
    async def register_specialization(self, specialization_id: str, specialization_config: Dict[str, Any], user_context: Dict[str, Any] = None) -> bool:
        """
        Register a new specialization.
        
        Args:
            specialization_id: Unique identifier for the specialization
            specialization_config: Specialization configuration
            user_context: User context for security and tenant validation
            
        Returns:
            True if registered successfully, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_specialization_start", success=True, details={"specialization_id": specialization_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "specialization_registry", "write"):
                        await self.record_health_metric("register_specialization_access_denied", 1.0, {"specialization_id": specialization_id})
                        await self.log_operation_with_telemetry("register_specialization_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_specialization_tenant_denied", 1.0, {"specialization_id": specialization_id})
                            await self.log_operation_with_telemetry("register_specialization_complete", success=False)
                            return False
            
            # Validate required fields
            required_fields = ["name", "description", "pillar", "capabilities", "system_prompt_template"]
            for field in required_fields:
                if field not in specialization_config:
                    await self.record_health_metric("register_specialization_validation_failed", 1.0, {"specialization_id": specialization_id, "missing_field": field})
                    await self.log_operation_with_telemetry("register_specialization_complete", success=False)
                    self.logger.error(f"Missing required field '{field}' in specialization config")
                    return False
            
            # Register specialization
            self.specializations[specialization_id] = specialization_config
            
            # Add to pillar specializations
            pillar = specialization_config["pillar"]
            if pillar not in self.pillar_specializations:
                self.pillar_specializations[pillar] = []
            
            if specialization_id not in self.pillar_specializations[pillar]:
                self.pillar_specializations[pillar].append(specialization_id)
            
            # Save to file
            self._save_specializations()
            
            # Record success metric
            await self.record_health_metric("register_specialization_success", 1.0, {"specialization_id": specialization_id, "pillar": pillar})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_specialization_complete", success=True, details={"specialization_id": specialization_id})
            
            self.logger.info(f"Registered specialization: {specialization_id}")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_specialization", details={"specialization_id": specialization_id})
            self.logger.error(f"Failed to register specialization {specialization_id}: {e}")
            return False
    
    def get_specialization(self, specialization_id: str) -> Optional[Dict[str, Any]]:
        """Get specialization configuration by ID."""
        return self.specializations.get(specialization_id)
    
    async def get_specializations_for_pillar(self, pillar: str, user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all specializations for a specific pillar."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_specializations_for_pillar_start", success=True, details={"pillar": pillar})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "specialization_registry", "read"):
                        await self.record_health_metric("get_specializations_for_pillar_access_denied", 1.0, {"pillar": pillar})
                        await self.log_operation_with_telemetry("get_specializations_for_pillar_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_specializations_for_pillar_tenant_denied", 1.0, {"pillar": pillar})
                            await self.log_operation_with_telemetry("get_specializations_for_pillar_complete", success=False)
                            return []
            
            specialization_ids = self.pillar_specializations.get(pillar, [])
            result = [
                {
                    "id": spec_id,
                    **self.specializations[spec_id]
                }
                for spec_id in specialization_ids
                if spec_id in self.specializations
            ]
            
            # Record success metric
            await self.record_health_metric("get_specializations_for_pillar_success", 1.0, {"pillar": pillar, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_specializations_for_pillar_complete", success=True, details={"pillar": pillar, "count": len(result)})
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_specializations_for_pillar", details={"pillar": pillar})
            self.logger.error(f"Failed to get specializations for pillar {pillar}: {e}")
            return []
    
    async def get_all_specializations(self, user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all available specializations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_all_specializations_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "specialization_registry", "read"):
                        await self.record_health_metric("get_all_specializations_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_all_specializations_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_all_specializations_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_all_specializations_complete", success=False)
                            return []
            
            result = [
                {
                    "id": spec_id,
                    **spec_config
                }
                for spec_id, spec_config in self.specializations.items()
            ]
            
            # Record success metric
            await self.record_health_metric("get_all_specializations_success", 1.0, {"count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_all_specializations_complete", success=True, details={"count": len(result)})
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_all_specializations")
            self.logger.error(f"Failed to get all specializations: {e}")
            return []
    
    async def validate_specialization(self, specialization_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate a specialization configuration.
        
        Args:
            specialization_id: Specialization ID to validate
            user_context: User context for security and tenant validation
            
        Returns:
            Validation result with details
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_specialization_start", success=True, details={"specialization_id": specialization_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "specialization_registry", "read"):
                        await self.record_health_metric("validate_specialization_access_denied", 1.0, {"specialization_id": specialization_id})
                        await self.log_operation_with_telemetry("validate_specialization_complete", success=False)
                        return {"valid": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("validate_specialization_tenant_denied", 1.0, {"specialization_id": specialization_id})
                            await self.log_operation_with_telemetry("validate_specialization_complete", success=False)
                            return {"valid": False, "error": "Tenant access denied"}
            
            if specialization_id not in self.specializations:
                await self.record_health_metric("validate_specialization_not_found", 1.0, {"specialization_id": specialization_id})
                await self.log_operation_with_telemetry("validate_specialization_complete", success=True)
                return {
                    "valid": False,
                    "error": f"Specialization '{specialization_id}' not found"
                }
            
            spec = self.specializations[specialization_id]
            errors = []
            
            # Check required fields
            required_fields = ["name", "description", "pillar", "capabilities", "system_prompt_template"]
            for field in required_fields:
                if field not in spec or not spec[field]:
                    errors.append(f"Missing or empty required field: {field}")
            
            # Check pillar validity
            valid_pillars = ["insights", "operations", "content", "experience"]
            if spec.get("pillar") not in valid_pillars:
                errors.append(f"Invalid pillar: {spec.get('pillar')}. Must be one of: {valid_pillars}")
            
            # Check capabilities format
            if "capabilities" in spec and not isinstance(spec["capabilities"], list):
                errors.append("Capabilities must be a list")
            
            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "specialization": spec
            }
            
            # Record success metric
            await self.record_health_metric("validate_specialization_success", 1.0, {"specialization_id": specialization_id, "valid": result["valid"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_specialization_complete", success=True, details={"specialization_id": specialization_id, "valid": result["valid"]})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_specialization", details={"specialization_id": specialization_id})
            return {
                "valid": False,
                "error": f"Validation failed: {e}"
            }
    
    async def search_specializations(self, query: str, pillar: str = None, user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search specializations by keywords or description.
        
        Args:
            query: Search query
            pillar: Optional pillar filter
            user_context: User context for security and tenant validation
            
        Returns:
            List of matching specializations
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("search_specializations_start", success=True, details={"query": query, "pillar": pillar})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "specialization_registry", "read"):
                        await self.record_health_metric("search_specializations_access_denied", 1.0, {"query": query})
                        await self.log_operation_with_telemetry("search_specializations_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("search_specializations_tenant_denied", 1.0, {"query": query})
                            await self.log_operation_with_telemetry("search_specializations_complete", success=False)
                            return []
            
            query_lower = query.lower()
            results = []
            
            for spec_id, spec in self.specializations.items():
                # Filter by pillar if specified
                if pillar and spec.get("pillar") != pillar:
                    continue
                
                # Search in name, description, and keywords
                searchable_text = " ".join([
                    spec.get("name", ""),
                    spec.get("description", ""),
                    " ".join(spec.get("keywords", []))
                ]).lower()
                
                if query_lower in searchable_text:
                    results.append({
                        "id": spec_id,
                        **spec
                    })
            
            # Record success metric
            await self.record_health_metric("search_specializations_success", 1.0, {"query": query, "results_count": len(results)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("search_specializations_complete", success=True, details={"results_count": len(results)})
            
            return results
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "search_specializations", details={"query": query, "pillar": pillar})
            self.logger.error(f"Search failed: {e}")
            return []
    
    async def remove_specialization(self, specialization_id: str, user_context: Dict[str, Any] = None) -> bool:
        """Remove a specialization."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("remove_specialization_start", success=True, details={"specialization_id": specialization_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "specialization_registry", "write"):
                        await self.record_health_metric("remove_specialization_access_denied", 1.0, {"specialization_id": specialization_id})
                        await self.log_operation_with_telemetry("remove_specialization_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("remove_specialization_tenant_denied", 1.0, {"specialization_id": specialization_id})
                            await self.log_operation_with_telemetry("remove_specialization_complete", success=False)
                            return False
            
            if specialization_id not in self.specializations:
                await self.record_health_metric("remove_specialization_not_found", 1.0, {"specialization_id": specialization_id})
                await self.log_operation_with_telemetry("remove_specialization_complete", success=True)
                return False
            
            # Remove from pillar specializations
            spec = self.specializations[specialization_id]
            pillar = spec.get("pillar")
            if pillar and specialization_id in self.pillar_specializations.get(pillar, []):
                self.pillar_specializations[pillar].remove(specialization_id)
            
            # Remove from specializations
            del self.specializations[specialization_id]
            
            # Save to file
            self._save_specializations()
            
            # Record success metric
            await self.record_health_metric("remove_specialization_success", 1.0, {"specialization_id": specialization_id, "pillar": pillar})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("remove_specialization_complete", success=True, details={"specialization_id": specialization_id})
            
            self.logger.info(f"Removed specialization: {specialization_id}")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "remove_specialization", details={"specialization_id": specialization_id})
            self.logger.error(f"Failed to remove specialization {specialization_id}: {e}")
            return False
    
    def get_specialization_stats(self) -> Dict[str, Any]:
        """Get specialization registry statistics."""
        try:
            total_specializations = len(self.specializations)
            pillar_counts = {
                pillar: len(specs) 
                for pillar, specs in self.pillar_specializations.items()
            }
            
            return {
                "total_specializations": total_specializations,
                "pillar_counts": pillar_counts,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}


# Global specialization registry instance (lazy initialization)
_specialization_registry: Optional[SpecializationRegistry] = None


def get_specialization_registry(di_container=None) -> Optional[SpecializationRegistry]:
    """
    Get the global specialization registry instance.
    
    Note: This is a legacy function. The registry should be obtained from
    AgenticFoundationService instead. This function is kept for backward compatibility.
    
    Args:
        di_container: DI Container (required for first call)
    
    Returns:
        SpecializationRegistry instance or None if di_container not provided
    """
    global _specialization_registry
    
    if _specialization_registry is None:
        if not di_container:
            # Return None instead of raising - let the caller handle it
            return None
        _specialization_registry = SpecializationRegistry(di_container=di_container)
    
    return _specialization_registry



