"""
Comprehensive unit tests for workflow file parsing.

Tests:
- BPMN file parsing (.bpmn)
- JSON workflow format (.json)
- Draw.io file parsing (.drawio)
- Node extraction
- Edge extraction
- Gateway extraction
- Error handling
"""

import pytest
import asyncio
import json
import xml.etree.ElementTree as ET
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.content
@pytest.mark.workflow_parsing
@pytest.mark.fast
class TestWorkflowParsing:
    """Test suite for workflow file parsing."""
    
    @pytest.fixture
    def mock_file_parser_service(self):
        """Create mock FileParserService."""
        service = Mock()
        service.logger = Mock()
        service.platform_gateway = Mock()
        service.realm_name = "business_enablement"
        service.utilities_module = Mock()
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        return service
    
    @pytest.fixture
    def workflow_parsing(self, mock_file_parser_service):
        """Create WorkflowParsing instance."""
        from backend.content.services.file_parser_service.modules.workflow_parsing import WorkflowParsing
        return WorkflowParsing(mock_file_parser_service)
    
    @pytest.fixture
    def sample_bpmn_data(self):
        """Sample BPMN XML data."""
        return b"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="Process_1">
    <bpmn:startEvent id="StartEvent_1"/>
    <bpmn:task id="Task_1" name="Task 1"/>
    <bpmn:endEvent id="EndEvent_1"/>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1"/>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="EndEvent_1"/>
  </bpmn:process>
</bpmn:definitions>"""
    
    @pytest.fixture
    def sample_json_workflow_data(self):
        """Sample JSON workflow data (React Flow format)."""
        workflow = {
            "nodes": [
                {"id": "1", "type": "input", "data": {"label": "Start"}},
                {"id": "2", "type": "default", "data": {"label": "Process"}},
                {"id": "3", "type": "output", "data": {"label": "End"}}
            ],
            "edges": [
                {"id": "e1-2", "source": "1", "target": "2"},
                {"id": "e2-3", "source": "2", "target": "3"}
            ]
        }
        return json.dumps(workflow).encode('utf-8')
    
    @pytest.fixture
    def sample_drawio_data(self):
        """Sample Draw.io XML data."""
        return b"""<mxfile>
  <diagram>
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" value="Start" vertex="1" parent="1"/>
        <mxCell id="3" value="Process" vertex="1" parent="1"/>
        <mxCell id="4" value="" edge="1" parent="1" source="2" target="3"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    
    @pytest.mark.asyncio
    async def test_parse_bpmn_file(self, workflow_parsing, mock_file_parser_service, sample_bpmn_data):
        """Test parsing BPMN file."""
        result = await workflow_parsing.parse(
            file_data=sample_bpmn_data,
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "workflow"
        assert result["file_type"] == "bpmn"
        assert "structure" in result
        assert "nodes" in result["structure"]
        assert "edges" in result["structure"]
        assert len(result["structure"]["nodes"]) > 0
    
    @pytest.mark.asyncio
    async def test_parse_json_workflow(self, workflow_parsing, mock_file_parser_service, sample_json_workflow_data):
        """Test parsing JSON workflow file."""
        result = await workflow_parsing.parse(
            file_data=sample_json_workflow_data,
            file_type="json",
            filename="test.json",
            parse_options={"is_workflow": True}
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "workflow"
        assert result["file_type"] == "json"
        assert "structure" in result
        assert "nodes" in result["structure"]
        assert "edges" in result["structure"]
        assert len(result["structure"]["nodes"]) == 3
        assert len(result["structure"]["edges"]) == 2
    
    @pytest.mark.asyncio
    async def test_parse_drawio_file(self, workflow_parsing, mock_file_parser_service, sample_drawio_data):
        """Test parsing Draw.io file."""
        result = await workflow_parsing.parse(
            file_data=sample_drawio_data,
            file_type="drawio",
            filename="test.drawio"
        )
        
        assert result["success"] is True
        assert result["parsing_type"] == "workflow"
        assert result["file_type"] == "drawio"
        assert "structure" in result
        assert "nodes" in result["structure"]
        assert "edges" in result["structure"]
    
    @pytest.mark.asyncio
    async def test_parse_unsupported_workflow_type(self, workflow_parsing, mock_file_parser_service):
        """Test parsing unsupported workflow file type."""
        result = await workflow_parsing.parse(
            file_data=b"test data",
            file_type="unknown",
            filename="test.unknown"
        )
        
        assert result["success"] is False
        assert result["error"] == "unsupported_file_type"
        assert "Unsupported workflow file type" in result["message"]
    
    @pytest.mark.asyncio
    async def test_bpmn_node_extraction(self, workflow_parsing, mock_file_parser_service, sample_bpmn_data):
        """Test BPMN node extraction."""
        result = await workflow_parsing.parse(
            file_data=sample_bpmn_data,
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        assert result["success"] is True
        nodes = result["structure"]["nodes"]
        assert len(nodes) > 0
        
        # Verify node types
        node_types = [node.get("type") for node in nodes]
        assert "startEvent" in node_types or "task" in node_types or "endEvent" in node_types
    
    @pytest.mark.asyncio
    async def test_bpmn_edge_extraction(self, workflow_parsing, mock_file_parser_service, sample_bpmn_data):
        """Test BPMN edge extraction."""
        result = await workflow_parsing.parse(
            file_data=sample_bpmn_data,
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        assert result["success"] is True
        edges = result["structure"]["edges"]
        assert len(edges) > 0
        
        # Verify edges have source and target
        for edge in edges:
            assert "source" in edge or "sourceRef" in edge
            assert "target" in edge or "targetRef" in edge
    
    @pytest.mark.asyncio
    async def test_bpmn_gateway_extraction(self, workflow_parsing, mock_file_parser_service):
        """Test BPMN gateway extraction."""
        bpmn_with_gateway = b"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="Process_1">
    <bpmn:startEvent id="StartEvent_1"/>
    <bpmn:exclusiveGateway id="Gateway_1"/>
    <bpmn:task id="Task_1" name="Task 1"/>
    <bpmn:endEvent id="EndEvent_1"/>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Gateway_1"/>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Gateway_1" targetRef="Task_1"/>
    <bpmn:sequenceFlow id="Flow_3" sourceRef="Task_1" targetRef="EndEvent_1"/>
  </bpmn:process>
</bpmn:definitions>"""
        
        result = await workflow_parsing.parse(
            file_data=bpmn_with_gateway,
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        assert result["success"] is True
        nodes = result["structure"]["nodes"]
        
        # Verify gateway is extracted
        gateway_types = [node.get("type") for node in nodes if "gateway" in node.get("type", "").lower()]
        assert len(gateway_types) > 0
    
    @pytest.mark.asyncio
    async def test_json_workflow_node_types(self, workflow_parsing, mock_file_parser_service, sample_json_workflow_data):
        """Test JSON workflow node type extraction."""
        result = await workflow_parsing.parse(
            file_data=sample_json_workflow_data,
            file_type="json",
            filename="test.json",
            parse_options={"is_workflow": True}
        )
        
        assert result["success"] is True
        nodes = result["structure"]["nodes"]
        
        # Verify node types are preserved
        node_types = [node.get("type") for node in nodes]
        assert "input" in node_types
        assert "default" in node_types
        assert "output" in node_types
    
    @pytest.mark.asyncio
    async def test_json_workflow_edge_connections(self, workflow_parsing, mock_file_parser_service, sample_json_workflow_data):
        """Test JSON workflow edge connections."""
        result = await workflow_parsing.parse(
            file_data=sample_json_workflow_data,
            file_type="json",
            filename="test.json",
            parse_options={"is_workflow": True}
        )
        
        assert result["success"] is True
        edges = result["structure"]["edges"]
        
        # Verify edges connect nodes correctly
        assert len(edges) == 2
        edge_sources = [edge.get("source") for edge in edges]
        edge_targets = [edge.get("target") for edge in edges]
        assert "1" in edge_sources
        assert "2" in edge_targets
    
    @pytest.mark.asyncio
    async def test_invalid_bpmn_xml(self, workflow_parsing, mock_file_parser_service):
        """Test parsing invalid BPMN XML."""
        invalid_bpmn = b"<invalid>xml</invalid>"
        
        result = await workflow_parsing.parse(
            file_data=invalid_bpmn,
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        # Should handle gracefully (either success with minimal structure or failure)
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_invalid_json_workflow(self, workflow_parsing, mock_file_parser_service):
        """Test parsing invalid JSON workflow."""
        invalid_json = b"{invalid json}"
        
        result = await workflow_parsing.parse(
            file_data=invalid_json,
            file_type="json",
            filename="test.json",
            parse_options={"is_workflow": True}
        )
        
        # Should handle gracefully
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_empty_workflow_file(self, workflow_parsing, mock_file_parser_service):
        """Test parsing empty workflow file."""
        result = await workflow_parsing.parse(
            file_data=b"",
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        # Should handle gracefully
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_workflow_metadata_extraction(self, workflow_parsing, mock_file_parser_service, sample_bpmn_data):
        """Test workflow metadata extraction."""
        result = await workflow_parsing.parse(
            file_data=sample_bpmn_data,
            file_type="bpmn",
            filename="test.bpmn"
        )
        
        assert result["success"] is True
        assert "metadata" in result
        assert "node_count" in result["structure"]
        assert "edge_count" in result["structure"]



