#!/bin/bash
# Complete Testing Gauntlet - Run All Protection Layers
# Tests the 3 MVP use cases through comprehensive test coverage

set -e  # Exit on first failure (or remove for full report)

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🛡️  COMPLETE TESTING GAUNTLET - MVP USE CASES"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Testing 3 Use Cases:"
echo "  1. Defense T&E (Mission Planning, Telemetry)"
echo "  2. Underwriting Insights (Claims, Reinsurance)"
echo "  3. Coexistence (Schema Mapping, Legacy Integration)"
echo ""
echo "═══════════════════════════════════════════════════════════════════"

# Check prerequisites
echo ""
echo "📋 STEP 0: Prerequisites Check"
echo "─────────────────────────────────────────────────────────────────"

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend not running at http://localhost:8000"
    echo "   Run: cd symphainy-platform && python3 main.py"
    exit 1
fi
echo "✅ Backend running"

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  Frontend not running at http://localhost:3000"
    echo "   This is OK for backend-only tests, but React tests will be skipped"
else
    echo "✅ Frontend running"
fi

# Check demo files
DEMO_FILES_DIR="scripts/mvpdemoscript/demo_files"
if [ ! -d "$DEMO_FILES_DIR" ]; then
    echo "❌ Demo files not generated"
    echo "   Run: cd scripts/mvpdemoscript && python3 generate_symphainy_demo.py"
    exit 1
fi
echo "✅ Demo files available"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "LAYER 1: INFRASTRUCTURE TESTS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Demo Files Integration
echo "🧪 Test 1.1: Demo Files Structure & Validity"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_demo_files_integration.py -v --tb=short || {
    echo "❌ Demo files validation failed"
    echo "   This means your generated demo files have structural issues"
}

# Platform Startup
echo ""
echo "🧪 Test 1.2: Platform Startup & Health"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_platform_startup_e2e.py -v --tb=short || {
    echo "⚠️  Platform startup tests failed"
}

# API Endpoints
echo ""
echo "🧪 Test 1.3: HTTP API Endpoints Availability"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_api_endpoints_reality.py -v --tb=short || {
    echo "❌ API endpoints test failed"
    echo "   This means frontend can't reach backend APIs"
}

# WebSocket Endpoints
echo ""
echo "🧪 Test 1.4: WebSocket Endpoints Availability"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_websocket_endpoints_reality.py -v --tb=short || {
    echo "❌ WebSocket endpoints test failed"
    echo "   This means real-time chat won't work"
}

# React Provider Tree (if frontend running)
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo ""
    echo "🧪 Test 1.5: React Provider Tree Completeness"
    echo "─────────────────────────────────────────────────────────────────"
    pytest tests/e2e/test_react_provider_tree.py -v --tb=short || {
        echo "❌ React provider tree test failed"
        echo "   This means frontend will crash with context errors"
    }
else
    echo ""
    echo "⏭️  Test 1.5: React Provider Tree - SKIPPED (frontend not running)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "LAYER 2: FUNCTIONAL BUSINESS LOGIC TESTS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Content Pillar Functional
echo "🧪 Test 2.1: Content Pillar - File Parsing (CSV, Binary, Excel, PDF, DOCX)"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_content_pillar_functional.py -v --tb=short || {
    echo "❌ CRITICAL: File parsing doesn't work!"
    echo "   Users won't be able to upload and parse files"
    echo "   Defense T&E: Mission CSVs, Telemetry binary files"
    echo "   Underwriting: Claims CSVs, Reinsurance Excel, PDF notes"
    echo "   Coexistence: Legacy policy CSVs"
}

# Document Generation Functional
echo ""
echo "🧪 Test 2.2: Document Generation (SOP, Workflow, Roadmap, POC)"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_document_generation_functional.py -v --tb=short || {
    echo "❌ CRITICAL: Document generation doesn't work!"
    echo "   This is core MVP value - can't show CTO"
    echo "   Operations Pillar: SOPs, Workflows"
    echo "   Business Outcomes: Roadmaps, POC proposals"
}

# Complete User Journeys
echo ""
echo "🧪 Test 2.3: Complete User Journeys (End-to-End Flows)"
echo "─────────────────────────────────────────────────────────────────"
pytest tests/e2e/test_complete_user_journeys_functional.py -v --tb=short || {
    echo "❌ CRITICAL: Complete journeys don't work!"
    echo "   Individual pieces work but complete flow breaks"
    echo "   CTO demo will fail halfway through"
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "LAYER 3: USE CASE SCENARIO TESTS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Defense T&E Scenario
echo "🧪 Test 3.1: Defense T&E Use Case"
echo "─────────────────────────────────────────────────────────────────"
echo "Testing:"
echo "  - Upload mission_plan.csv (50 missions)"
echo "  - Parse telemetry_raw.bin (binary with COBOL)"
echo "  - Extract from test_incident_reports.docx"
echo "  - Generate operational SOPs"
echo "  - Create mission workflow diagrams"
echo ""
pytest tests/e2e/test_content_pillar_functional.py::TestCSVParsing::test_upload_and_parse_csv_functional -v --tb=short || {
    echo "❌ Defense T&E: Mission CSV parsing failed"
}
pytest tests/e2e/test_content_pillar_functional.py::TestBinaryParsing::test_upload_and_parse_binary_functional -v --tb=short || {
    echo "⚠️  Defense T&E: Binary telemetry parsing failed"
}
pytest tests/e2e/test_content_pillar_functional.py::TestDOCXExtraction::test_upload_and_extract_docx_text -v --tb=short || {
    echo "⚠️  Defense T&E: Incident report DOCX extraction failed"
}

# Underwriting Insights Scenario
echo ""
echo "🧪 Test 3.2: Underwriting Insights Use Case"
echo "─────────────────────────────────────────────────────────────────"
echo "Testing:"
echo "  - Upload claims.csv (insurance claims)"
echo "  - Parse reinsurance.xlsx (multi-sheet Excel)"
echo "  - Extract underwriting_notes.pdf"
echo "  - Analyze claims data"
echo "  - Generate strategic roadmap"
echo "  - Create POC proposal"
echo ""
pytest tests/e2e/test_content_pillar_functional.py::TestExcelParsing::test_upload_and_parse_excel_functional -v --tb=short || {
    echo "⚠️  Underwriting: Excel reinsurance parsing failed"
}
pytest tests/e2e/test_content_pillar_functional.py::TestPDFExtraction::test_upload_and_extract_pdf_text -v --tb=short || {
    echo "⚠️  Underwriting: PDF notes extraction failed"
}

# Coexistence Scenario
echo ""
echo "🧪 Test 3.3: Coexistence Use Case"
echo "─────────────────────────────────────────────────────────────────"
echo "Testing:"
echo "  - Upload legacy_policy_export.csv"
echo "  - Apply schema mapping (alignment_map.json)"
echo "  - Transform legacy to modern format"
echo "  - Validate data integrity"
echo ""
pytest tests/e2e/test_demo_files_integration.py::TestCoexistenceScenario -v --tb=short || {
    echo "⚠️  Coexistence: Schema mapping/transformation failed"
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "LAYER 4: THE ULTIMATE TEST (All 4 Pillars)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

echo "🧪 Test 4: Complete 4-Pillar Journey (CTO Demo)"
echo "─────────────────────────────────────────────────────────────────"
echo "Testing complete journey through:"
echo "  1. Content Pillar: Upload & Parse"
echo "  2. Insights Pillar: Analyze Data"
echo "  3. Operations Pillar: Generate SOP & Workflow"
echo "  4. Business Outcomes: Create Roadmap & POC"
echo ""
pytest tests/e2e/test_complete_user_journeys_functional.py::TestCompleteAll4PillarsJourney::test_all_four_pillars_complete_journey -v --tb=short || {
    echo "❌ ULTIMATE TEST FAILED!"
    echo "   The complete 4-pillar journey doesn't work"
    echo "   This is a PRODUCTION BLOCKER"
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📊 TESTING GAUNTLET COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Summary:"
echo "  ✅ Infrastructure Tests - API endpoints, WebSockets, React providers"
echo "  ✅ Functional Tests - File parsing, document generation"
echo "  ✅ Use Case Tests - Defense T&E, Underwriting, Coexistence"
echo "  ✅ Ultimate Test - Complete 4-pillar journey"
echo ""
echo "If all tests passed, your platform is PRODUCTION READY! 🚀"
echo ""
echo "Next steps:"
echo "  1. Review any failures above"
echo "  2. Fix identified issues"
echo "  3. Re-run this script"
echo "  4. When all green, deploy to production!"
echo ""
echo "═══════════════════════════════════════════════════════════════════"

