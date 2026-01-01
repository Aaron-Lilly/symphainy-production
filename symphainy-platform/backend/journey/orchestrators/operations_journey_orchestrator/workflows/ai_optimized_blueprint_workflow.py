#!/usr/bin/env python3
"""
AI-Optimized Blueprint Workflow

WHAT: Orchestrates AI-optimized coexistence blueprint generation from available documents
HOW: Data mash queries + Agent critical reasoning + Blueprint optimization

This workflow implements the AI-optimized blueprint generation flow:
1. Query data mash for available SOP/workflow files
2. Agent critical reasoning (OperationsSpecialistAgent) - analyzes documents
3. Generate optimized blueprint with recommendations
4. Create implementation roadmap
5. Solution context integration for enhanced prompting
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class AIOptimizedBlueprintWorkflow:
    """
    Workflow for generating AI-optimized coexistence blueprints.
    
    Uses agentic-forward pattern:
    - Agent does critical reasoning first
    - Service executes based on agent's strategic decisions
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: OperationsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        sop_file_ids: Optional[List[str]] = None,
        workflow_file_ids: Optional[List[str]] = None,
        optimization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute AI-optimized blueprint generation workflow.
        
        Args:
            sop_file_ids: Optional list of SOP file IDs to use
            workflow_file_ids: Optional list of workflow file IDs to use
            optimization_options: Optional optimization options
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with blueprint_structure, recommendations, roadmap, etc.
        """
        try:
            self.logger.info("📊 Starting AI-optimized blueprint generation workflow")
            
            # Generate workflow ID
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            
            # Step 1: Query data mash for available SOP/workflow files
            available_documents = []
            
            # Get Data Solution Orchestrator
            curator = await self.orchestrator.get_foundation_service("CuratorFoundationService")
            if curator:
                data_orchestrator = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                if data_orchestrator:
                    # Query for workflow/SOP files
                    self.logger.info("📊 Querying data mash for available workflow/SOP files")
                    mash_result = await data_orchestrator.orchestrate_data_mash(
                        client_data_query={"type": "workflow_sop"},
                        user_context=user_context
                    )
                    
                    if mash_result.get("success"):
                        client_data = mash_result.get("client_data", {})
                        workflow_sop_data = client_data.get("workflow_sop", {})
                        
                        # Collect available documents
                        if not sop_file_ids:
                            sop_files = workflow_sop_data.get("sop_files", [])
                            sop_parsed = workflow_sop_data.get("sop_parsed", [])
                            available_documents.extend(sop_files)
                            available_documents.extend(sop_parsed)
                        
                        if not workflow_file_ids:
                            workflow_files = workflow_sop_data.get("workflow_files", [])
                            workflow_parsed = workflow_sop_data.get("workflow_parsed", [])
                            available_documents.extend(workflow_files)
                            available_documents.extend(workflow_parsed)
            
            # Step 2: If specific file IDs provided, fetch those documents
            selected_documents = []
            
            if sop_file_ids or workflow_file_ids:
                # Fetch specific documents
                if curator and data_orchestrator:
                    for file_id in (sop_file_ids or []):
                        file_result = await data_orchestrator.orchestrate_data_mash(
                            client_data_query={"type": "file_id:" + file_id},
                            user_context=user_context
                        )
                        if file_result.get("success"):
                            file_data = file_result.get("client_data", {})
                            file = file_data.get("file")
                            if file:
                                # Add parsed files to the file document
                                parsed_files = file_data.get("parsed_files", [])
                                if parsed_files:
                                    file["parsed_files"] = parsed_files
                                selected_documents.append(file)
                            else:
                                self.logger.error(f"❌ Data mash query succeeded but no file data returned for file_id: {file_id}")
                        else:
                            error_msg = file_result.get("error", "Unknown error")
                            self.logger.error(f"❌ Data mash query failed for file_id {file_id}: {error_msg}")
                    
                    for file_id in (workflow_file_ids or []):
                        file_result = await data_orchestrator.orchestrate_data_mash(
                            client_data_query={"type": "file_id:" + file_id},
                            user_context=user_context
                        )
                        if file_result.get("success"):
                            file_data = file_result.get("client_data", {})
                            file = file_data.get("file")
                            if file:
                                # Add parsed files to the file document
                                parsed_files = file_data.get("parsed_files", [])
                                if parsed_files:
                                    file["parsed_files"] = parsed_files
                                selected_documents.append(file)
                            else:
                                self.logger.error(f"❌ Data mash query succeeded but no file data returned for file_id: {file_id}")
                        else:
                            error_msg = file_result.get("error", "Unknown error")
                            self.logger.error(f"❌ Data mash query failed for file_id {file_id}: {error_msg}")
                else:
                    self.logger.error("❌ Curator or Data Orchestrator not available - cannot fetch specific files")
            
            # Combine available and selected documents
            all_documents = available_documents + selected_documents
            
            # If specific file IDs were provided, verify we found them
            # DO NOT create placeholders - if files aren't found, that's a real platform issue
            missing_file_ids = []
            if sop_file_ids or workflow_file_ids:
                # Track which file IDs we actually found
                existing_file_ids = {doc.get("file_id") or doc.get("uuid") or doc.get("id") for doc in all_documents}
                
                # Check for missing files
                for file_id in (sop_file_ids or []):
                    if file_id not in existing_file_ids:
                        missing_file_ids.append(f"SOP file: {file_id}")
                        self.logger.error(f"❌ File {file_id} not found in data mash - this is a platform issue that must be fixed")
                
                for file_id in (workflow_file_ids or []):
                    if file_id not in existing_file_ids:
                        missing_file_ids.append(f"Workflow file: {file_id}")
                        self.logger.error(f"❌ File {file_id} not found in data mash - this is a platform issue that must be fixed")
            
            # If specific files were requested but not found, return error
            if missing_file_ids:
                return {
                    "success": False,
                    "error": f"Requested files not found in data mash: {', '.join(missing_file_ids)}. This indicates a platform issue with file storage or retrieval that must be fixed.",
                    "workflow_id": workflow_id,
                    "missing_files": missing_file_ids
                }
            
            if not all_documents:
                return {
                    "success": False,
                    "error": "No workflow/SOP documents available for blueprint generation",
                    "workflow_id": workflow_id
                }
            
            self.logger.info(f"📊 Found {len(all_documents)} documents for blueprint generation")
            
            # Step 3: Get Operations Specialist Agent
            specialist_agent = await self.orchestrator._get_operations_specialist_agent()
            if not specialist_agent:
                return {
                    "success": False,
                    "error": "Operations Specialist Agent not available",
                    "workflow_id": workflow_id
                }
            
            # Step 4: Agent critical reasoning - analyze documents and generate optimized blueprint
            self.logger.info("🤖 Agent critical reasoning: Analyzing documents and generating optimized blueprint")
            
            # Enhance context with solution context if available
            enhanced_context = (optimization_options or {}).copy()
            if user_context and user_context.get("solution_context"):
                solution_context = user_context["solution_context"]
                enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
            
            # Prepare document content for agent
            document_content = {
                "documents": all_documents,
                "sop_count": len([d for d in all_documents if d.get("file_type_category") == "sop" or d.get("parsing_type") == "sop"]),
                "workflow_count": len([d for d in all_documents if d.get("file_type_category") == "workflow" or d.get("parsing_type") == "workflow"])
            }
            
            # Extract SOP and workflow content from documents
            sop_content = {}
            workflow_content = {}
            sop_file_ids_found = []
            workflow_file_ids_found = []
            
            for doc in all_documents:
                # Check file metadata for type
                file_type_category = doc.get("file_type_category") or doc.get("metadata", {}).get("file_type_category")
                parsing_type = doc.get("parsing_type") or doc.get("metadata", {}).get("parsing_type")
                file_id = doc.get("file_id") or doc.get("uuid") or doc.get("id")
                
                # Get parsed files from doc or from data mash result
                parsed_files = doc.get("parsed_files", [])
                if not parsed_files and doc.get("parsed_file_id"):
                    # Try to get parsed file details
                    if curator and data_orchestrator:
                        parsed_result = await data_orchestrator.orchestrate_data_mash(
                            client_data_query={"type": "parsed_file_id:" + doc.get("parsed_file_id")},
                            user_context=user_context
                        )
                        if parsed_result.get("success"):
                            parsed_files = parsed_result.get("client_data", {}).get("parsed_files", [])
                
                if file_type_category == "sop" or parsing_type == "sop":
                    if file_id:
                        sop_file_ids_found.append(file_id)
                    # Get parsed SOP structure
                    if parsed_files:
                        for pf in parsed_files:
                            parse_result = pf.get("metadata", {}).get("parse_result", {})
                            if not parse_result:
                                parse_result = pf.get("parse_result", {})
                            if parse_result.get("parsing_type") == "sop":
                                sop_content = parse_result.get("structure", {})
                                break
                    # Fallback: use file metadata if available
                    if not sop_content and doc.get("metadata", {}).get("parse_result", {}).get("parsing_type") == "sop":
                        sop_content = doc.get("metadata", {}).get("parse_result", {}).get("structure", {})
                elif file_type_category == "workflow" or parsing_type == "workflow":
                    if file_id:
                        workflow_file_ids_found.append(file_id)
                    # Get parsed workflow structure
                    if parsed_files:
                        for pf in parsed_files:
                            parse_result = pf.get("metadata", {}).get("parse_result", {})
                            if not parse_result:
                                parse_result = pf.get("parse_result", {})
                            if parse_result.get("parsing_type") == "workflow":
                                workflow_content = parse_result.get("structure", {})
                                break
                    # Fallback: use file metadata if available
                    if not workflow_content and doc.get("metadata", {}).get("parse_result", {}).get("parsing_type") == "workflow":
                        workflow_content = doc.get("metadata", {}).get("parse_result", {}).get("structure", {})
            
            # Verify we actually extracted content from the documents
            # DO NOT create fake content - if extraction fails, that's a real platform issue
            content_extraction_errors = []
            
            if sop_file_ids_found and not sop_content:
                content_extraction_errors.append(
                    f"Failed to extract SOP content from files: {', '.join(sop_file_ids_found)}. "
                    "This indicates a platform issue with file parsing or content extraction."
                )
                self.logger.error(f"❌ SOP content extraction failed for files: {sop_file_ids_found}")
            
            if workflow_file_ids_found and not workflow_content:
                content_extraction_errors.append(
                    f"Failed to extract workflow content from files: {', '.join(workflow_file_ids_found)}. "
                    "This indicates a platform issue with file parsing or content extraction."
                )
                self.logger.error(f"❌ Workflow content extraction failed for files: {workflow_file_ids_found}")
            
            # If we have file IDs but no content, return error
            if content_extraction_errors:
                return {
                    "success": False,
                    "error": "Content extraction failed. " + " ".join(content_extraction_errors),
                    "workflow_id": workflow_id,
                    "extraction_errors": content_extraction_errors
                }
            
            # If no files were found at all, return error
            if not sop_content and not workflow_content:
                return {
                    "success": False,
                    "error": "No SOP or workflow content could be extracted from available documents. "
                             "This indicates a platform issue with document parsing or data mash queries.",
                    "workflow_id": workflow_id
                }
            
            reasoning_result = await specialist_agent.analyze_for_coexistence_structure(
                sop_content=sop_content,
                workflow_content=workflow_content,
                context=enhanced_context,
                user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
            )
            
            if not reasoning_result.get("success"):
                return {
                    "success": False,
                    "error": "Agent reasoning failed",
                    "workflow_id": workflow_id,
                    "reasoning_error": reasoning_result.get("error")
                }
            
            coexistence_structure = reasoning_result.get("coexistence_structure", {})
            reasoning = reasoning_result.get("reasoning", {})
            recommendations = reasoning.get("recommendations", []) if isinstance(reasoning, dict) else []
            
            self.logger.info("✅ Agent reasoning complete: Generated optimized coexistence structure")
            
            # Step 5: Execute blueprint generation using CoexistenceAnalysisService
            coexistence_service = await self.orchestrator._get_coexistence_analysis_service()
            if coexistence_service:
                self.logger.info("⚙️ Executing blueprint generation via CoexistenceAnalysisService")
                
                # Build current and target states from documents
                current_state = {
                    "sop_content": sop_content,
                    "workflow_content": workflow_content,
                    "documents": all_documents
                }
                target_state = {
                    "coexistence_structure": coexistence_structure,
                    "optimization_goals": enhanced_context.get("user_goals", "")
                }
                
                # Build SOP and workflow content for service
                sop_content_for_service = current_state.get("sop_content", {})
                workflow_content_for_service = current_state.get("workflow_content", {})
                
                # Convert sop_content to string if it's a dict
                sop_content_str = str(sop_content_for_service) if isinstance(sop_content_for_service, dict) else (sop_content_for_service or "")
                
                service_result = await coexistence_service.analyze_coexistence(
                    coexistence_structure=coexistence_structure,
                    sop_content=sop_content_str,
                    workflow_content=workflow_content_for_service,
                    options=optimization_options,
                    user_context=user_context
                )
                
                if service_result.get("success"):
                    # Merge service result with agent reasoning
                    blueprint_structure = service_result.get("blueprint", {})
                    if not blueprint_structure:
                        blueprint_structure = {
                            "coexistence_structure": coexistence_structure,
                            "current_state": current_state,
                            "target_state": target_state
                        }
                    recommendations = service_result.get("recommendations", recommendations)
                else:
                    # Build blueprint structure from agent reasoning
                    blueprint_structure = {
                        "coexistence_structure": coexistence_structure,
                        "current_state": current_state,
                        "target_state": target_state
                    }
            else:
                # Build blueprint structure from agent reasoning only
                blueprint_structure = {
                    "coexistence_structure": coexistence_structure,
                    "current_state": {"sop_content": sop_content, "workflow_content": workflow_content},
                    "target_state": {"coexistence_structure": coexistence_structure}
                }
            
            # Build implementation roadmap from recommendations
            implementation_roadmap = {
                "phases": [
                    {
                        "phase": 1,
                        "name": "Assessment",
                        "steps": recommendations[:3] if len(recommendations) >= 3 else recommendations
                    },
                    {
                        "phase": 2,
                        "name": "Implementation",
                        "steps": recommendations[3:6] if len(recommendations) >= 6 else recommendations[3:] if len(recommendations) > 3 else []
                    },
                    {
                        "phase": 3,
                        "name": "Optimization",
                        "steps": recommendations[6:] if len(recommendations) > 6 else []
                    }
                ]
            }
            
            # Step 6: Build result
            result = {
                "success": True,
                "blueprint_structure": blueprint_structure,
                "recommendations": recommendations,
                "implementation_roadmap": implementation_roadmap,
                "workflow_id": workflow_id,
                "agent_reasoning": reasoning if isinstance(reasoning, dict) else {"analysis": str(reasoning)},
                "documents_used": {
                    "count": len(all_documents),
                    "sop_count": document_content["sop_count"],
                    "workflow_count": document_content["workflow_count"]
                }
            }
            
            self.logger.info(f"✅ AI-optimized blueprint generation complete: workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ AI-optimized blueprint generation workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }

