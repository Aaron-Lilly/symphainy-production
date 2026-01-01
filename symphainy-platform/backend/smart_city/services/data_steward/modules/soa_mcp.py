#!/usr/bin/env python3
"""
Data Steward Service - SOA/MCP Module

Micro-module for SOA API exposure and MCP tool integration.
"""

from typing import Any, Dict


class SoaMcp:
    """SOA/MCP module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for realm consumption (Phase 3.3: Data Steward Finalization)."""
        self.service.soa_apis = {
            # Semantic Contract APIs
            "create_semantic_contract": {
                "endpoint": "/api/data-steward/contracts",
                "method": "POST",
                "description": "Create semantic contract",
                "parameters": ["contract_data", "user_context"]
            },
            "get_semantic_contract": {
                "endpoint": "/api/data-steward/contracts/{contract_id}",
                "method": "GET",
                "description": "Get semantic contract by ID",
                "parameters": ["contract_id", "user_context"]
            },
            "update_semantic_contract": {
                "endpoint": "/api/data-steward/contracts/{contract_id}",
                "method": "PUT",
                "description": "Update semantic contract",
                "parameters": ["contract_id", "contract_updates", "user_context"]
            },
            "validate_semantic_contract": {
                "endpoint": "/api/data-steward/contracts/{contract_id}/validate",
                "method": "POST",
                "description": "Validate semantic contract",
                "parameters": ["contract_id", "data", "user_context"]
            },
            # Governance APIs
            "create_data_policy": {
                "endpoint": "/api/data-steward/policies",
                "method": "POST",
                "description": "Create data policy",
                "parameters": ["policy_data", "user_context"]
            },
            "get_data_policy": {
                "endpoint": "/api/data-steward/policies/{policy_id}",
                "method": "GET",
                "description": "Get data policy by ID",
                "parameters": ["policy_id", "user_context"]
            },
            "enforce_data_policy": {
                "endpoint": "/api/data-steward/policies/{policy_id}/enforce",
                "method": "POST",
                "description": "Enforce data policy",
                "parameters": ["policy_id", "resource_id", "user_context"]
            },
            # Lineage APIs
            "track_lineage": {
                "endpoint": "/api/data-steward/lineage",
                "method": "POST",
                "description": "Track data lineage",
                "parameters": ["lineage_data", "user_context"]
            },
            "get_lineage": {
                "endpoint": "/api/data-steward/lineage/{asset_id}",
                "method": "GET",
                "description": "Get lineage for asset",
                "parameters": ["asset_id", "user_context"]
            },
            "query_lineage": {
                "endpoint": "/api/data-steward/lineage/query",
                "method": "POST",
                "description": "Query lineage with filters",
                "parameters": ["filters", "user_context"]
            },
            # WAL APIs (for governance and audit)
            "write_to_log": {
                "endpoint": "/api/data-steward/wal/write",
                "method": "POST",
                "description": "Write operation to WAL for audit and durability",
                "parameters": ["namespace", "payload", "target", "lifecycle"]
            },
            "replay_log": {
                "endpoint": "/api/data-steward/wal/replay",
                "method": "POST",
                "description": "Replay operations from WAL for recovery",
                "parameters": ["namespace", "from_timestamp", "to_timestamp", "filters"]
            },
            "update_log_status": {
                "endpoint": "/api/data-steward/wal/status",
                "method": "PUT",
                "description": "Update WAL entry status after operation execution",
                "parameters": ["log_id", "status", "result", "error"]
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ SOA APIs exposed: {len(self.service.soa_apis)} endpoints")
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for agent access."""
        self.service.mcp_tools = {
            "create_content_policy": {
                "name": "create_content_policy",
                "description": "Create a content policy for a specific data type",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data_type": {"type": "string", "description": "Type of data to create policy for"},
                        "rules": {"type": "object", "description": "Policy rules and constraints"}
                    },
                    "required": ["data_type", "rules"]
                }
            },
            "get_policy_for_content": {
                "name": "get_policy_for_content",
                "description": "Get policy for a specific content type",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string", "description": "Content type to get policy for"}
                    },
                    "required": ["content_type"]
                }
            },
            "record_lineage": {
                "name": "record_lineage",
                "description": "Record data lineage information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lineage_data": {"type": "object", "description": "Lineage data to record"}
                    },
                    "required": ["lineage_data"]
                }
            },
            "get_lineage": {
                "name": "get_lineage",
                "description": "Get lineage information for an asset",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset ID to get lineage for"}
                    },
                    "required": ["asset_id"]
                }
            },
            "validate_schema": {
                "name": "validate_schema",
                "description": "Validate data schema",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "schema_data": {"type": "object", "description": "Schema data to validate"}
                    },
                    "required": ["schema_data"]
                }
            },
            "get_quality_metrics": {
                "name": "get_quality_metrics",
                "description": "Get quality metrics for an asset",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset ID to get quality metrics for"}
                    },
                    "required": ["asset_id"]
                }
            },
            "enforce_compliance": {
                "name": "enforce_compliance",
                "description": "Enforce compliance rules for an asset",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset ID to enforce compliance for"},
                        "compliance_rules": {"type": "array", "description": "Compliance rules to enforce"}
                    },
                    "required": ["asset_id", "compliance_rules"]
                }
            },
            "write_to_log": {
                "name": "write_to_log",
                "description": "Write operation to WAL for audit and durability",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "namespace": {"type": "string", "description": "Logical group (e.g., saga_execution, canonical_model)"},
                        "payload": {"type": "object", "description": "Operation data to log"},
                        "target": {"type": "string", "description": "Where to send after logging (queue, topic, service)"},
                        "lifecycle": {"type": "object", "description": "Retry count, delay, TTL, backoff strategy"}
                    },
                    "required": ["namespace", "payload", "target"]
                }
            },
            "replay_log": {
                "name": "replay_log",
                "description": "Replay operations from WAL for recovery or audit",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "namespace": {"type": "string", "description": "Logical group to replay"},
                        "from_timestamp": {"type": "string", "description": "Start timestamp (ISO format)"},
                        "to_timestamp": {"type": "string", "description": "End timestamp (ISO format)"},
                        "filters": {"type": "object", "description": "Additional filters (operation, target, status, correlation_id)"}
                    },
                    "required": ["namespace", "from_timestamp", "to_timestamp"]
                }
            }
        }
        
        self.service.mcp_server_enabled = True
        
        if self.service.logger:
            self.service.logger.info(f"✅ MCP tools registered: {len(self.service.mcp_tools)} tools")
    
    async def register_capabilities(self) -> Dict[str, Any]:
        """Register Data Steward capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
        try:
            # Build capabilities list with SOA API and MCP Tool contracts
            capabilities = []
            
            # Create policy_management capability
            capabilities.append({
                "name": "policy_management",
                "protocol": "DataStewardServiceProtocol",
                "description": "Content policy creation and management",
                "contracts": {
                    "soa_api": {
                        "api_name": "create_content_policy",
                        "endpoint": self.service.soa_apis.get("create_content_policy", {}).get("endpoint", "/soa/data-steward/create_content_policy"),
                        "method": self.service.soa_apis.get("create_content_policy", {}).get("method", "POST"),
                        "handler": getattr(self.service, "create_content_policy", None),
                        "metadata": {
                            "description": "Create content policy for data type",
                            "apis": ["create_content_policy", "get_policy_for_content"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "data_steward_create_content_policy",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "data_steward_create_content_policy",
                            "description": "Create a content policy for a specific data type",
                            "input_schema": self.service.mcp_tools.get("create_content_policy", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create lineage_tracking capability
            capabilities.append({
                "name": "lineage_tracking",
                "protocol": "DataStewardServiceProtocol",
                "description": "Data lineage tracking and retrieval",
                "contracts": {
                    "soa_api": {
                        "api_name": "record_lineage",
                        "endpoint": self.service.soa_apis.get("record_lineage", {}).get("endpoint", "/soa/data-steward/record_lineage"),
                        "method": self.service.soa_apis.get("record_lineage", {}).get("method", "POST"),
                        "handler": getattr(self.service, "record_lineage", None),
                        "metadata": {
                            "description": "Record data lineage",
                            "apis": ["record_lineage", "get_lineage"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "data_steward_record_lineage",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "data_steward_record_lineage",
                            "description": "Record data lineage information",
                            "input_schema": self.service.mcp_tools.get("record_lineage", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create quality_compliance capability
            capabilities.append({
                "name": "quality_compliance",
                "protocol": "DataStewardServiceProtocol",
                "description": "Data quality validation and compliance enforcement",
                "contracts": {
                    "soa_api": {
                        "api_name": "validate_schema",
                        "endpoint": self.service.soa_apis.get("validate_schema", {}).get("endpoint", "/soa/data-steward/validate_schema"),
                        "method": self.service.soa_apis.get("validate_schema", {}).get("method", "POST"),
                        "handler": getattr(self.service, "validate_schema", None),
                        "metadata": {
                            "description": "Validate data schema",
                            "apis": ["validate_schema", "get_quality_metrics", "enforce_compliance"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "data_steward_validate_schema",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "data_steward_validate_schema",
                            "description": "Validate data schema",
                            "input_schema": self.service.mcp_tools.get("validate_schema", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create write_ahead_logging capability ⭐ NEW
            capabilities.append({
                "name": "write_ahead_logging",
                "protocol": "DataStewardServiceProtocol",
                "description": "Write-Ahead Logging for audit trail and durability",
                "contracts": {
                    "soa_api": {
                        "api_name": "write_to_log",
                        "endpoint": self.service.soa_apis.get("write_to_log", {}).get("endpoint", "/soa/data-steward/wal/write"),
                        "method": self.service.soa_apis.get("write_to_log", {}).get("method", "POST"),
                        "handler": getattr(self.service, "write_to_log", None),
                        "metadata": {
                            "description": "Write-Ahead Logging for governance",
                            "apis": ["write_to_log", "replay_log", "update_log_status"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "data_steward_write_to_log",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "data_steward_write_to_log",
                            "description": "Write operation to WAL for audit and durability",
                            "input_schema": self.service.mcp_tools.get("write_to_log", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Register using register_with_curator (simplified Phase 2 pattern)
            soa_api_names = list(self.service.soa_apis.keys())
            mcp_tool_names = [f"data_steward_{tool}" for tool in self.service.mcp_tools.keys()]
            
            success = await self.service.register_with_curator(
                capabilities=capabilities,
                soa_apis=soa_api_names,
                mcp_tools=mcp_tool_names,
                protocols=[{
                    "name": "DataStewardServiceProtocol",
                    "definition": {
                        "methods": {api: {"input_schema": {}, "output_schema": {}} for api in soa_api_names}
                    }
                }]
            )
            
            if success:
                if self.service.logger:
                    self.service.logger.info(f"✅ Data Steward registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Failed to register Data Steward with Curator")
                    
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to register Data Steward capabilities: {e}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return capabilities metadata
        return await self._get_data_steward_capabilities_dict()
    
    async def _get_data_steward_capabilities_dict(self) -> Dict[str, Any]:
        """Get Data Steward capabilities metadata dict."""
        return {
            "policy_management": {
                "create_content_policy": True,
                "get_policy_for_content": True
            },
            "lineage_tracking": {
                "record_lineage": True,
                "get_lineage": True
            },
            "quality_compliance": {
                "validate_schema": True,
                "get_quality_metrics": True,
                "enforce_compliance": True
            },
            "infrastructure": {
                "knowledge_governance": True,
                "state_management": True,
                "messaging_cache": True
            }
        }






