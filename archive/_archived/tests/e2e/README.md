# E2E Tests for Symphainy Platform

This directory contains comprehensive End-to-End (E2E) tests for the Symphainy Platform, specifically focusing on the Content Pillar functionality.

## Overview

The E2E test suite validates the complete user journey from the landing page through file upload, parsing, and interaction with the Content Pillar. It ensures that all components work together correctly in a real browser environment.

## Test Structure

```
tests/e2e/
├── README.md                           # This file
├── test_content_pillar_e2e.py          # Main test suite
├── test_content_pillar_test_cases.py   # Individual test case methods
├── test_data_generator.py              # Test data generation utilities
├── test_config.py                      # Test configuration management
├── test_utilities.py                   # Test utility functions
├── run_e2e_tests.py                    # Main test runner
├── validate_setup.py                   # Setup validation script
├── test_data/                          # Generated test data files
├── test_reports/                       # Test execution reports
├── test_screenshots/                   # Screenshots on failure
└── test_videos/                        # Video recordings (optional)
```

## Test Cases

### Content Pillar E2E Tests

1. **Landing Page GuideAgent Interaction**
   - Verifies landing page elements and GuideAgent functionality
   - Tests user goal input and agent suggestions
   - Validates navigation to Content Pillar

2. **Content Pillar Dashboard View**
   - Tests dashboard display of available files
   - Verifies file uploader functionality
   - Checks navigation elements

3. **CSV File Upload and Parsing**
   - Tests CSV file upload process
   - Validates data parsing to parquet format
   - Verifies data preview functionality

4. **JSON File Upload and Parsing**
   - Tests JSON file upload process
   - Validates data parsing to JSON Structured format
   - Verifies structured data preview

5. **Mainframe Binary File Upload**
   - Tests mainframe binary file (.dat) upload
   - Validates copybook (.cpy) upload
   - Tests COBOL2CSV conversion process
   - Verifies converted data preview

6. **ContentLiaisonAgent Interaction**
   - Tests agent interaction with parsed files
   - Validates agent responses to data questions
   - Verifies agent guidance functionality

7. **Data Preparation for Insights Pillar**
   - Tests file preparation for next pillar
   - Validates data format requirements
   - Tests navigation to Insights Pillar

8. **Error Handling and Validation**
   - Tests invalid file type handling
   - Validates error message display
   - Tests corrupted file handling

9. **File Management Operations**
   - Tests file deletion functionality
   - Validates file renaming
   - Tests file details view
   - Verifies re-parsing with different formats

## Prerequisites

### Required Dependencies

```bash
# Install Python dependencies
pip install playwright pytest asyncio

# Install Playwright browsers
playwright install
```

### Required Services

The following services must be running for E2E tests:

1. **Frontend Application** (symphainy-frontend)
   - URL: http://localhost:3000
   - Must be running and accessible

2. **Backend Services**
   - Experience Service: http://localhost:8003
   - Content Pillar Service: http://localhost:8001
   - Business Orchestrator: http://localhost:8000

3. **Smart City Services**
   - Traffic Cop Service
   - Post Office Service
   - Librarian Service

## Configuration

### Environment Variables

Set the following environment variables:

```bash
# Frontend URLs
FRONTEND_BASE_URL=http://localhost:3000
CONTENT_PILLAR_URL=http://localhost:3000/content

# Backend URLs
BACKEND_BASE_URL=http://localhost:8000
CONTENT_PILLAR_SERVICE_URL=http://localhost:8001
EXPERIENCE_SERVICE_URL=http://localhost:8003

# Test Settings
TEST_ENVIRONMENT=test
TEST_DEBUG_MODE=false
TEST_VERBOSE_LOGGING=false
```

### Configuration Files

The test suite uses `test_config.py` for configuration management. You can:

1. Use default configuration
2. Load from JSON file: `--config config.json`
3. Override with command line arguments

## Running Tests

### Quick Start

```bash
# Validate setup
python validate_setup.py

# Run all tests
python run_e2e_tests.py

# Run with specific environment
python run_e2e_tests.py --environment development

# Run in headless mode
python run_e2e_tests.py --headless

# Run with debugging
python run_e2e_tests.py --debug --verbose
```

### Command Line Options

```bash
python run_e2e_tests.py --help
```

Available options:
- `--environment, -e`: Test environment (test, development, staging, production)
- `--config, -c`: Configuration file path
- `--headless`: Run in headless mode
- `--debug`: Enable debug mode
- `--verbose`: Enable verbose logging
- `--screenshot`: Take screenshots
- `--video`: Record video
- `--report-dir`: Report directory
- `--test-files-dir`: Test files directory

### Running Specific Tests

```bash
# Run only Content Pillar tests
python run_e2e_tests.py --environment test

# Run with specific configuration
python run_e2e_tests.py --config my_config.json
```

## Test Data

### Generated Test Files

The test suite automatically generates realistic test data:

- **test_customers.csv**: 100 customer records with realistic data
- **test_customers.json**: Same data in JSON format
- **test_payments.csv**: 200 payment records
- **test_payments.json**: Same data in JSON format
- **test_mainframe.dat**: 50 mainframe binary records
- **test_copybook.cpy**: COBOL copybook for mainframe data
- **invalid_file.txt**: For error testing
- **corrupted.csv**: For error testing

### Custom Test Data

You can provide custom test data by:

1. Placing files in the `test_data/` directory
2. Modifying `test_data_generator.py` to generate different data
3. Using the `--test-files-dir` option to specify a different directory

## Reports and Artifacts

### Test Reports

The test suite generates comprehensive reports:

- **HTML Report**: `test_reports/test_report_YYYYMMDD_HHMMSS.html`
- **JSON Report**: `test_reports/test_report_YYYYMMDD_HHMMSS.json`

### Screenshots

Screenshots are taken on test failures:
- Location: `test_screenshots/`
- Format: `failure_test_name_YYYYMMDD_HHMMSS.png`

### Videos

Optional video recording:
- Location: `test_videos/`
- Format: MP4 files for each test

## Debugging

### Debug Mode

Run tests in debug mode for detailed logging:

```bash
python run_e2e_tests.py --debug --verbose
```

### Screenshots

Take screenshots during test execution:

```bash
python run_e2e_tests.py --screenshot
```

### Browser Debugging

Run tests with visible browser for debugging:

```bash
python run_e2e_tests.py --environment development
```

## Troubleshooting

### Common Issues

1. **Browser not found**
   ```bash
   playwright install
   ```

2. **Services not running**
   - Ensure all required services are running
   - Check service URLs in configuration

3. **Test data not found**
   - Run `python validate_setup.py` to generate test data
   - Check `test_data/` directory

4. **Import errors**
   - Ensure project root is in Python path
   - Check all dependencies are installed

### Validation

Always run setup validation before executing tests:

```bash
python validate_setup.py
```

This will check:
- Dependencies
- Test structure
- Imports
- Configuration
- Test data generation

## Contributing

### Adding New Tests

1. Add test methods to `test_content_pillar_test_cases.py`
2. Update `test_content_pillar_e2e.py` to include new tests
3. Add test data if needed in `test_data_generator.py`
4. Update this README with new test descriptions

### Test Naming Convention

- Test methods should start with `test_`
- Use descriptive names: `test_file_upload_csv`
- Group related tests in the same class

### Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Clean up test data after each test
3. **Assertions**: Use specific, meaningful assertions
4. **Error Handling**: Test both success and failure scenarios
5. **Performance**: Monitor test execution time

## Integration with CI/CD

### GitHub Actions

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      - name: Start services
        run: |
          # Start your services here
      - name: Run E2E tests
        run: |
          cd tests/e2e
          python run_e2e_tests.py --headless
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: e2e-reports
          path: tests/e2e/test_reports/
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install'
            }
        }
        stage('Start Services') {
            steps {
                // Start your services
            }
        }
        stage('E2E Tests') {
            steps {
                dir('tests/e2e') {
                    sh 'python run_e2e_tests.py --headless'
                }
            }
        }
        stage('Publish Reports') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'tests/e2e/test_reports',
                    reportFiles: 'test_report_*.html',
                    reportName: 'E2E Test Report'
                ])
            }
        }
    }
}
```

## Support

For issues or questions about the E2E test suite:

1. Check the troubleshooting section above
2. Run `python validate_setup.py` to validate setup
3. Check test reports for detailed error information
4. Review logs in `e2e_test.log`

## License

This E2E test suite is part of the Symphainy Platform project and follows the same license terms.





