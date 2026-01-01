#!/usr/bin/env python3
"""
Test Session & State Orchestration Capabilities

Tests the new architecturally-aligned session and state management:
1. Session creation with orchestrator context
2. Conversation tracking (guide agent and liaison agents)
3. Orchestrator workflow tracking
4. Session state retrieval with orchestrator states
5. End-to-end flow validation
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import platform components
from backend.experience.services.session_manager_service.session_manager_service import SessionManagerService
from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter


class Colors:
    """Terminal colors for output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


async def test_session_creation():
    """Test 1: Session creation with orchestrator context."""
    print_header("TEST 1: Session Creation with Orchestrator Context")
    
    try:
        # Get shared session manager (creates it if needed)
        session_manager = await get_shared_session_manager()
        
        print_success("Session Manager initialized")
        
        # Create session
        result = await session_manager.create_session(
            user_id="test_user_123",
            context={"test": "context"}
        )
        
        if not result.get("success"):
            print_error(f"Session creation failed: {result.get('error')}")
            return False
        
        session = result.get("session", {})
        session_id = session.get("session_id")
        
        if not session_id:
            print_error("Session ID not returned")
            return False
        
        print_success(f"Session created: {session_id}")
        
        # Verify orchestrator context exists
        orchestrator_context = session.get("orchestrator_context", {})
        if not orchestrator_context:
            print_error("Orchestrator context not in session")
            return False
        
        print_success("Orchestrator context present in session")
        print_info(f"  Active orchestrators: {len(orchestrator_context.get('active_orchestrators', []))}")
        print_info(f"  Enabling services: {len(orchestrator_context.get('enabling_services', {}))}")
        
        # Verify conversations dict exists
        conversations = session.get("conversations", {})
        if not isinstance(conversations, dict):
            print_error("Conversations not a dict in session")
            return False
        
        print_success("Conversations dict present in session")
        print_info(f"  Conversation types: {list(conversations.keys())}")
        
        return True, session_id
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_conversation_tracking(session_id: str):
    """Test 2: Conversation tracking for guide agent."""
    print_header("TEST 2: Conversation Tracking (Guide Agent)")
    
    try:
        # Get shared session manager
        session_manager = await get_shared_session_manager()
        
        # Add user message
        print_info("Adding user message to guide_agent conversation...")
        result = await session_manager.add_conversation_message(
            session_id=session_id,
            agent_type="guide_agent",
            role="user",
            content="I want to upload a file for analysis"
        )
        
        if not result.get("success"):
            print_error(f"Failed to add user message: {result.get('error')}")
            return False
        
        print_success("User message added to conversation")
        
        # Add assistant response with orchestrator context
        print_info("Adding assistant response with orchestrator context...")
        result = await session_manager.add_conversation_message(
            session_id=session_id,
            agent_type="guide_agent",
            role="assistant",
            content="I'll help you upload a file. Routing to Content Analysis Orchestrator.",
            orchestrator_context={
                "orchestrator": "ContentAnalysisOrchestrator",
                "workflow_id": "test_workflow_123",
                "status": "active"
            }
        )
        
        if not result.get("success"):
            print_error(f"Failed to add assistant message: {result.get('error')}")
            return False
        
        print_success("Assistant message added with orchestrator context")
        
        # Retrieve conversation history
        print_info("Retrieving conversation history...")
        history_result = await session_manager.get_conversation_history(
            session_id=session_id,
            agent_type="guide_agent"
        )
        
        if not history_result.get("success"):
            print_error(f"Failed to get conversation history: {history_result.get('error')}")
            return False
        
        messages = history_result.get("messages", [])
        if len(messages) != 2:
            print_error(f"Expected 2 messages, got {len(messages)}")
            return False
        
        print_success(f"Conversation history retrieved: {len(messages)} messages")
        
        # Verify orchestrator context in last message
        last_message = messages[-1]
        if last_message.get("role") != "assistant":
            print_error("Last message should be assistant")
            return False
        
        orchestrator_context = last_message.get("orchestrator_context")
        if not orchestrator_context:
            print_error("Orchestrator context not in assistant message")
            return False
        
        if orchestrator_context.get("orchestrator") != "ContentAnalysisOrchestrator":
            print_error(f"Wrong orchestrator: {orchestrator_context.get('orchestrator')}")
            return False
        
        print_success("Orchestrator context verified in conversation")
        print_info(f"  Orchestrator: {orchestrator_context.get('orchestrator')}")
        print_info(f"  Workflow ID: {orchestrator_context.get('workflow_id')}")
        print_info(f"  Status: {orchestrator_context.get('status')}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_liaison_conversation_tracking(session_id: str):
    """Test 3: Conversation tracking for liaison agent."""
    print_header("TEST 3: Conversation Tracking (Liaison Agent)")
    
    try:
        # Get shared session manager
        session_manager = await get_shared_session_manager()
        
        # Add user message to content_liaison
        print_info("Adding user message to content_liaison conversation...")
        result = await session_manager.add_conversation_message(
            session_id=session_id,
            agent_type="content_liaison",
            role="user",
            content="How do I upload a PDF file?"
        )
        
        if not result.get("success"):
            print_error(f"Failed to add user message: {result.get('error')}")
            return False
        
        print_success("User message added to content_liaison conversation")
        
        # Add assistant response
        print_info("Adding assistant response...")
        result = await session_manager.add_conversation_message(
            session_id=session_id,
            agent_type="content_liaison",
            role="assistant",
            content="You can upload a PDF file using the file upload interface. I'll process it through the Content Analysis Orchestrator.",
            orchestrator_context={
                "orchestrator": "ContentAnalysisOrchestrator",
                "status": "active"
            }
        )
        
        if not result.get("success"):
            print_error(f"Failed to add assistant message: {result.get('error')}")
            return False
        
        print_success("Assistant message added to content_liaison conversation")
        
        # Retrieve conversation history
        history_result = await session_manager.get_conversation_history(
            session_id=session_id,
            agent_type="content_liaison"
        )
        
        if not history_result.get("success"):
            print_error(f"Failed to get conversation history: {history_result.get('error')}")
            return False
        
        messages = history_result.get("messages", [])
        print_success(f"Content liaison conversation history: {len(messages)} messages")
        
        # Verify both conversations exist
        session_result = await session_manager.get_session(session_id)
        if not session_result.get("success"):
            print_error("Failed to get session")
            return False
        
        session = session_result.get("session", {})
        conversations = session.get("conversations", {})
        
        if "guide_agent" not in conversations:
            print_error("guide_agent conversation not found")
            return False
        
        if "content_liaison" not in conversations:
            print_error("content_liaison conversation not found")
            return False
        
        print_success("Multiple agent conversations tracked in session")
        print_info(f"  Guide Agent messages: {len(conversations.get('guide_agent', {}).get('messages', []))}")
        print_info(f"  Content Liaison messages: {len(conversations.get('content_liaison', {}).get('messages', []))}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator_workflow_tracking(session_id: str):
    """Test 4: Orchestrator workflow tracking."""
    print_header("TEST 4: Orchestrator Workflow Tracking")
    
    try:
        # Get shared session manager
        session_manager = await get_shared_session_manager()
        
        # Track workflow start
        print_info("Tracking workflow start...")
        workflow_data = {
            "workflow_id": "upload_test_file_123",
            "status": "processing",
            "started_at": datetime.utcnow().isoformat(),
            "enabling_services": ["ContentSteward"],
            "operation": "file_upload",
            "filename": "test_file.pdf"
        }
        
        result = await session_manager.track_orchestrator_workflow(
            session_id=session_id,
            orchestrator_name="ContentAnalysisOrchestrator",
            workflow_data=workflow_data
        )
        
        if not result.get("success"):
            print_error(f"Failed to track workflow: {result.get('error')}")
            return False
        
        print_success("Workflow start tracked")
        
        # Get orchestrator state (for specific orchestrator)
        print_info("Retrieving orchestrator state...")
        state_result = await session_manager.get_orchestrator_state(
            session_id=session_id,
            orchestrator_name="ContentAnalysisOrchestrator"
        )
        
        if not state_result.get("success"):
            print_error(f"Failed to get orchestrator state: {state_result.get('error')}")
            return False
        
        # Get full session to check active orchestrators
        session_result = await session_manager.get_session(session_id)
        if not session_result.get("success"):
            print_error("Failed to get session")
            return False
        
        session = session_result.get("session", {})
        orchestrator_context = session.get("orchestrator_context", {})
        active_orchestrators = orchestrator_context.get("active_orchestrators", [])
        
        if len(active_orchestrators) == 0:
            print_error("No active orchestrators found")
            return False
        
        print_success(f"Orchestrator state retrieved: {len(active_orchestrators)} active orchestrator(s)")
        
        # Find ContentAnalysisOrchestrator
        content_orch = None
        for orch in active_orchestrators:
            if orch.get("orchestrator_name") == "ContentAnalysisOrchestrator":
                content_orch = orch
                break
        
        if not content_orch:
            print_error("ContentAnalysisOrchestrator not found in active orchestrators")
            return False
        
        print_success("ContentAnalysisOrchestrator found in active orchestrators")
        print_info(f"  Status: {content_orch.get('status')}")
        print_info(f"  Workflow ID: {content_orch.get('workflow_id')}")
        print_info(f"  Started at: {content_orch.get('started_at')}")
        
        # Track workflow completion
        print_info("Tracking workflow completion...")
        completion_data = {
            "workflow_id": "upload_test_file_123",
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "file_id": "file_abc123"
        }
        
        result = await session_manager.track_orchestrator_workflow(
            session_id=session_id,
            orchestrator_name="ContentAnalysisOrchestrator",
            workflow_data=completion_data
        )
        
        if not result.get("success"):
            print_error(f"Failed to track workflow completion: {result.get('error')}")
            return False
        
        print_success("Workflow completion tracked")
        
        # Verify updated state (get full session)
        session_result = await session_manager.get_session(session_id)
        if not session_result.get("success"):
            print_error("Failed to get session")
            return False
        
        session = session_result.get("session", {})
        orchestrator_context = session.get("orchestrator_context", {})
        active_orchestrators = orchestrator_context.get("active_orchestrators", [])
        
        content_orch = None
        for orch in active_orchestrators:
            if orch.get("orchestrator_name") == "ContentAnalysisOrchestrator":
                content_orch = orch
                break
        
        if not content_orch:
            print_error("ContentAnalysisOrchestrator not found after completion")
            return False
        
        if content_orch.get("status") != "completed":
            print_error(f"Expected status 'completed', got '{content_orch.get('status')}'")
            return False
        
        print_success("Workflow status updated to 'completed'")
        print_info(f"  Completed at: {content_orch.get('completed_at')}")
        print_info(f"  File ID: {content_orch.get('file_id')}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_session_state_retrieval(session_id: str):
    """Test 5: Session state retrieval with orchestrator states."""
    print_header("TEST 5: Session State Retrieval")
    
    try:
        # Get shared session manager
        session_manager = await get_shared_session_manager()
        
        # Get full session
        print_info("Retrieving full session state...")
        result = await session_manager.get_session(session_id)
        
        if not result.get("success"):
            print_error(f"Failed to get session: {result.get('error')}")
            return False
        
        session = result.get("session", {})
        
        # Verify all components
        checks = {
            "session_id": session.get("session_id"),
            "user_id": session.get("user_id"),
            "orchestrator_context": session.get("orchestrator_context"),
            "conversations": session.get("conversations")
        }
        
        for key, value in checks.items():
            if value is None:
                print_error(f"Missing {key} in session")
                return False
            print_success(f"{key} present in session")
        
        # Verify orchestrator states
        orchestrator_context = session.get("orchestrator_context", {})
        active_orchestrators = orchestrator_context.get("active_orchestrators", [])
        
        print_success(f"Session state complete")
        print_info(f"  Session ID: {session.get('session_id')}")
        print_info(f"  User ID: {session.get('user_id')}")
        print_info(f"  Active orchestrators: {len(active_orchestrators)}")
        print_info(f"  Conversation types: {list(session.get('conversations', {}).keys())}")
        
        # Count total messages across all conversations
        total_messages = 0
        for conv_type, conv_data in session.get("conversations", {}).items():
            messages = conv_data.get("messages", [])
            total_messages += len(messages)
            print_info(f"    {conv_type}: {len(messages)} messages")
        
        print_success(f"Total messages across all conversations: {total_messages}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Shared session manager instance
_shared_session_manager = None

async def get_shared_session_manager():
    """Get or create shared session manager instance."""
    global _shared_session_manager
    if _shared_session_manager is None:
        di_container = DIContainerService(realm_name="experience")
        class MockPlatformGateway:
            pass
        _shared_session_manager = SessionManagerService(
            service_name="SessionManagerService",
            realm_name="experience",
            platform_gateway=MockPlatformGateway(),
            di_container=di_container
        )
        await _shared_session_manager.initialize()
    return _shared_session_manager


async def run_all_tests():
    """Run all tests in sequence."""
    print_header("SESSION & STATE ORCHESTRATION TEST SUITE")
    print_info("Testing new architecturally-aligned session and state management capabilities\n")
    
    results = {}
    
    # Test 1: Session Creation
    success, session_id = await test_session_creation()
    results["Session Creation"] = success
    if not success or not session_id:
        print_error("Cannot continue without a valid session")
        return False
    
    # Test 2: Guide Agent Conversation Tracking
    results["Guide Agent Conversations"] = await test_conversation_tracking(session_id)
    
    # Test 3: Liaison Agent Conversation Tracking
    results["Liaison Agent Conversations"] = await test_liaison_conversation_tracking(session_id)
    
    # Test 4: Orchestrator Workflow Tracking
    results["Orchestrator Workflow Tracking"] = await test_orchestrator_workflow_tracking(session_id)
    
    # Test 5: Session State Retrieval
    results["Session State Retrieval"] = await test_session_state_retrieval(session_id)
    
    # Summary
    print_header("TEST SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    print()
    if all_passed:
        print_success("🎉 ALL TESTS PASSED!")
        print_info("Session and state orchestration capabilities are working correctly.")
    else:
        print_error("❌ SOME TESTS FAILED")
        print_warning("Please review the errors above.")
    
    return all_passed


if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

