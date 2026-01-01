"""
E2E Test: Demo Files Integration
Tests MVP functionality using actual generated demo files
"""

import pytest
from pathlib import Path
import zipfile
import shutil

# Demo files location
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")

DEMO_FILES = {
    "defense": DEMO_FILES_DIR / "SymphAIny_Demo_Defense_TnE.zip",
    "underwriting": DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights.zip",
    "coexistence": DEMO_FILES_DIR / "SymphAIny_Demo_Coexistence.zip",
}

@pytest.fixture(scope="module")
def verify_demo_files_exist():
    """Verify all demo files are available"""
    missing_files = []
    for name, filepath in DEMO_FILES.items():
        if not filepath.exists():
            missing_files.append(f"{name}: {filepath}")
    
    if missing_files:
        pytest.skip(f"Demo files not found: {', '.join(missing_files)}")
    
    return True

@pytest.fixture
def test_workspace(tmp_path):
    """Create temporary workspace for extracting demo files"""
    workspace = tmp_path / "demo_workspace"
    workspace.mkdir()
    return workspace

class TestDefenseScenario:
    """Test Defense T&E scenario files"""
    
    def test_defense_zip_structure(self, verify_demo_files_exist):
        """Verify Defense ZIP contains expected files"""
        zip_path = DEMO_FILES["defense"]
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            
            # Check for expected files
            assert any('mission_plan.csv' in f for f in files), "mission_plan.csv missing"
            assert any('telemetry_raw.bin' in f for f in files), "telemetry_raw.bin missing"
            assert any('telemetry_copybook.cpy' in f for f in files), "copybook missing"
            assert any('test_incident_reports.docx' in f for f in files), "DOCX missing"
            assert any('ai_insights.json' in f for f in files), "insights JSON missing"
    
    def test_defense_csv_parseable(self, verify_demo_files_exist, test_workspace):
        """Verify mission_plan.csv is valid CSV"""
        import csv
        
        with zipfile.ZipFile(DEMO_FILES["defense"], 'r') as zf:
            zf.extractall(test_workspace)
        
        # Find the CSV file
        csv_file = list(test_workspace.rglob("mission_plan.csv"))[0]
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) > 0, "CSV has no data rows"
            assert 'mission_id' in rows[0], "CSV missing mission_id column"
            assert 'location' in rows[0], "CSV missing location column"
    
    def test_defense_binary_data(self, verify_demo_files_exist, test_workspace):
        """Verify telemetry binary file exists and has data"""
        with zipfile.ZipFile(DEMO_FILES["defense"], 'r') as zf:
            zf.extractall(test_workspace)
        
        bin_file = list(test_workspace.rglob("telemetry_raw.bin"))[0]
        
        assert bin_file.stat().st_size > 0, "Binary file is empty"
        
        # Verify it's binary data (not text)
        with open(bin_file, 'rb') as f:
            data = f.read(100)
            # Binary data should have non-printable characters
            assert not all(32 <= b < 127 or b in (9, 10, 13) for b in data), \
                "File appears to be text, not binary"

class TestUnderwritingScenario:
    """Test Underwriting Insights scenario files"""
    
    def test_underwriting_zip_structure(self, verify_demo_files_exist):
        """Verify Underwriting ZIP contains expected files"""
        zip_path = DEMO_FILES["underwriting"]
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            
            assert any('policy_master.dat' in f for f in files), "policy_master.dat missing"
            assert any('claims.csv' in f for f in files), "claims.csv missing"
            assert any('reinsurance.xlsx' in f for f in files), "Excel file missing"
            assert any('underwriting_notes.pdf' in f for f in files), "PDF missing"
            assert any('copybook.cpy' in f for f in files), "copybook missing"
    
    def test_underwriting_csv_parseable(self, verify_demo_files_exist, test_workspace):
        """Verify claims.csv is valid and has expected volume"""
        import csv
        
        with zipfile.ZipFile(DEMO_FILES["underwriting"], 'r') as zf:
            zf.extractall(test_workspace)
        
        csv_file = list(test_workspace.rglob("claims.csv"))[0]
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) > 1000, f"Expected >1000 rows, got {len(rows)}"
            assert 'policy_id' in rows[0], "CSV missing policy_id"
            assert 'claim_amount' in rows[0], "CSV missing claim_amount"
    
    def test_underwriting_excel_readable(self, verify_demo_files_exist, test_workspace):
        """Verify Excel file can be opened"""
        import pandas as pd
        
        with zipfile.ZipFile(DEMO_FILES["underwriting"], 'r') as zf:
            zf.extractall(test_workspace)
        
        excel_file = list(test_workspace.rglob("reinsurance.xlsx"))[0]
        
        df = pd.read_excel(excel_file)
        assert len(df) > 0, "Excel file has no data"
        assert 'policy_id' in df.columns, "Excel missing policy_id column"
    
    def test_underwriting_pdf_exists(self, verify_demo_files_exist, test_workspace):
        """Verify PDF file exists and has content"""
        with zipfile.ZipFile(DEMO_FILES["underwriting"], 'r') as zf:
            zf.extractall(test_workspace)
        
        pdf_file = list(test_workspace.rglob("underwriting_notes.pdf"))[0]
        
        assert pdf_file.stat().st_size > 1000, "PDF file seems too small"
        
        # Verify it's a PDF by checking header
        with open(pdf_file, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF', "File is not a valid PDF"

class TestCoexistenceScenario:
    """Test Pre-Migration Coexistence scenario files"""
    
    def test_coexistence_zip_structure(self, verify_demo_files_exist):
        """Verify Coexistence ZIP contains expected files"""
        zip_path = DEMO_FILES["coexistence"]
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            
            assert any('legacy_policy_export.csv' in f for f in files), "legacy CSV missing"
            assert any('target_schema.json' in f for f in files), "target schema missing"
            assert any('alignment_map.json' in f for f in files), "alignment map missing"
    
    def test_coexistence_schema_valid_json(self, verify_demo_files_exist, test_workspace):
        """Verify schema files are valid JSON"""
        import json
        
        with zipfile.ZipFile(DEMO_FILES["coexistence"], 'r') as zf:
            zf.extractall(test_workspace)
        
        # Test target schema
        schema_file = list(test_workspace.rglob("target_schema.json"))[0]
        with open(schema_file, 'r') as f:
            schema = json.load(f)
            assert isinstance(schema, dict), "Schema should be a dictionary"
            assert len(schema) > 0, "Schema is empty"
        
        # Test alignment map
        alignment_file = list(test_workspace.rglob("alignment_map.json"))[0]
        with open(alignment_file, 'r') as f:
            alignment = json.load(f)
            assert isinstance(alignment, dict), "Alignment map should be a dictionary"
    
    def test_coexistence_csv_matches_schema(self, verify_demo_files_exist, test_workspace):
        """Verify CSV fields match alignment map"""
        import csv
        import json
        
        with zipfile.ZipFile(DEMO_FILES["coexistence"], 'r') as zf:
            zf.extractall(test_workspace)
        
        # Load CSV
        csv_file = list(test_workspace.rglob("legacy_policy_export.csv"))[0]
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            csv_fields = reader.fieldnames
        
        # Load alignment map
        alignment_file = list(test_workspace.rglob("alignment_map.json"))[0]
        with open(alignment_file, 'r') as f:
            alignment = json.load(f)
        
        # Verify mapped fields exist in CSV
        for source_field in alignment.keys():
            assert source_field in csv_fields, \
                f"Alignment map references {source_field} but it's not in CSV"

class TestDemoFilesSizes:
    """Test that demo files are reasonable sizes"""
    
    def test_defense_size(self, verify_demo_files_exist):
        """Verify Defense ZIP is ~44KB"""
        size_kb = DEMO_FILES["defense"].stat().st_size / 1024
        assert 30 < size_kb < 100, f"Defense ZIP size unexpected: {size_kb:.1f}KB"
    
    def test_underwriting_size(self, verify_demo_files_exist):
        """Verify Underwriting ZIP is ~639KB"""
        size_kb = DEMO_FILES["underwriting"].stat().st_size / 1024
        assert 500 < size_kb < 1000, f"Underwriting ZIP size unexpected: {size_kb:.1f}KB"
    
    def test_coexistence_size(self, verify_demo_files_exist):
        """Verify Coexistence ZIP is ~3.7KB"""
        size_kb = DEMO_FILES["coexistence"].stat().st_size / 1024
        assert 1 < size_kb < 10, f"Coexistence ZIP size unexpected: {size_kb:.1f}KB"

class TestAllDemoFiles:
    """Test all demo files together"""
    
    def test_all_files_extractable(self, verify_demo_files_exist, test_workspace):
        """Verify all ZIP files can be extracted without errors"""
        for name, zip_path in DEMO_FILES.items():
            extract_dir = test_workspace / name
            extract_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Verify files were extracted
            extracted_files = list(extract_dir.rglob("*"))
            assert len(extracted_files) > 5, \
                f"{name} extracted fewer files than expected"
    
    def test_all_files_have_insights(self, verify_demo_files_exist, test_workspace):
        """Verify all scenarios include ai_insights.json"""
        import json
        
        for name, zip_path in DEMO_FILES.items():
            extract_dir = test_workspace / name
            extract_dir.mkdir()
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            insights_file = list(extract_dir.rglob("ai_insights.json"))
            assert len(insights_file) > 0, f"{name} missing ai_insights.json"
            
            with open(insights_file[0], 'r') as f:
                insights = json.load(f)
                assert isinstance(insights, dict), "Insights should be a dictionary"
                assert len(insights) > 0, "Insights is empty"

@pytest.mark.integration
class TestDemoFilesWithPlatform:
    """Integration tests - requires platform to be running"""
    
    @pytest.mark.skip(reason="Requires running platform - enable for integration testing")
    def test_upload_defense_file(self):
        """Test uploading Defense file to platform"""
        # This would test the actual API endpoint
        # Will implement when platform is running
        pass
    
    @pytest.mark.skip(reason="Requires running platform - enable for integration testing")
    def test_parse_all_file_types(self):
        """Test parsing all file types in demo files"""
        # This would test CSV, Binary, DOCX, PDF, XLSX, JSON parsing
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

