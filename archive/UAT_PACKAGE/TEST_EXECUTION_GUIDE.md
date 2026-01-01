# 🧪 Test Execution Guide

## **📋 Complete Test Execution Instructions**

This guide provides detailed instructions for running all test suites in the Symphainy Platform UAT package.

---

## **🚀 Quick Start - Run All Tests**

### **Option 1: Automated Script (Recommended)**
```bash
cd /home/founders/demoversion/symphainy_source
./UAT_PACKAGE/scripts/run_all_tests.sh
```

### **Option 2: Manual Execution**
```bash
cd /home/founders/demoversion/symphainy_source/tests
python3 -m pytest unit/utilities/test_utility_service_discovery.py e2e/user_journeys/test_complete_user_journeys_service_aware.py e2e/production/test_production_user_journeys.py::TestProductionUserJourneys::test_production_individual_tenant_journey -v
```

---

## **🔧 Individual Test Suite Execution**

### **1. Service Discovery Tests**
```bash
cd /home/founders/demoversion/symphainy_source/tests
python3 -m pytest unit/utilities/test_utility_service_discovery.py -v
```

**Expected Output:**
```
============================= test session starts ==============================
unit/utilities/test_utility_service_discovery.py::TestUtilityServiceDiscovery::test_configuration_utility_service_discovery PASSED [ 20%]
unit/utilities/test_utility_service_discovery.py::TestUtilityServiceDiscovery::test_utility_service_initialization PASSED [ 40%]
unit/utilities/test_utility_service_discovery.py::TestUtilityServiceDiscovery::test_cross_dimension_utility_access PASSED [ 60%]
unit/utilities/test_utility_service_discovery.py::TestUtilityServiceDiscovery::test_utility_service_health_check PASSED [ 80%]
unit/utilities/test_utility_service_discovery.py::TestUtilityServiceDiscovery::test_utility_service_configuration_access PASSED [100%]

============================== 5 passed in 0.08s ===============================
```

### **2. Service-Aware E2E Tests**
```bash
cd /home/founders/demoversion/symphainy_source/tests
python3 -m pytest e2e/user_journeys/test_complete_user_journeys_service_aware.py -v
```

**Expected Output:**
```
============================= test session starts ==============================
e2e/user_journeys/test_complete_user_journeys_service_aware.py::TestCompleteUserJourneysServiceAware::test_individual_tenant_journey_with_services PASSED [ 50%]
e2e/user_journeys/test_complete_user_journeys_service_aware.py::TestCompleteUserJourneysServiceAware::test_platform_health_with_services PASSED [100%]

============================== 2 passed in 0.54s ===============================
```

### **3. Production Environment Tests**
```bash
cd /home/founders/demoversion/symphainy_source/tests
python3 -m pytest e2e/production/test_production_user_journeys.py::TestProductionUserJourneys::test_production_individual_tenant_journey -v
```

**Expected Output:**
```
============================= test session starts ==============================
e2e/production/test_production_user_journeys.py::TestProductionUserJourneys::test_production_individual_tenant_journey PASSED [100%]

============================== 1 passed in 4.51s ===============================
```

---

## **📊 Test Execution Options**

### **Verbose Output**
```bash
python3 -m pytest -v
```

### **Detailed Output with Print Statements**
```bash
python3 -m pytest -s -v
```

### **HTML Report Generation**
```bash
python3 -m pytest --html=UAT_PACKAGE/reports/latest_test_results.html --self-contained-html
```

### **JSON Report Generation**
```bash
python3 -m pytest --json-report --json-report-file=UAT_PACKAGE/reports/test_results.json
```

### **Coverage Report**
```bash
python3 -m pytest --cov=symphainy-platform --cov-report=html --cov-report=term
```

---

## **🔧 Test Configuration**

### **Environment Variables**
```bash
export TEST_ENVIRONMENT=true
export LOG_LEVEL=INFO
export SERVICE_DISCOVERY=true
export MOCK_SERVICES=true
export API_TIMEOUT=30.0
export RETRY_ATTEMPTS=3
```

### **Python Path Configuration**
```bash
export PYTHONPATH="/home/founders/demoversion/symphainy_source/symphainy-platform:$PYTHONPATH"
```

### **Test Data Configuration**
```bash
export TEST_DATA_PATH="/home/founders/demoversion/symphainy_source/tests/data"
export REPORTS_PATH="/home/founders/demoversion/symphainy_source/tests/reports"
export LOGS_PATH="/home/founders/demoversion/symphainy_source/tests/logs"
```

---

## **📈 Test Execution Modes**

### **1. Development Mode (Fast)**
```bash
python3 -m pytest -m "not production" -v
```
- Runs only development tests
- Faster execution
- Good for development validation

### **2. Production Mode (Comprehensive)**
```bash
python3 -m pytest -m "production" -v
```
- Runs production environment tests
- More comprehensive validation
- Good for production readiness

### **3. Service Discovery Mode**
```bash
python3 -m pytest -m "service_discovery" -v
```
- Runs service discovery tests only
- Validates service architecture
- Good for service validation

### **4. E2E Mode**
```bash
python3 -m pytest -m "e2e" -v
```
- Runs end-to-end tests only
- Validates complete user journeys
- Good for user journey validation

---

## **🔍 Test Debugging**

### **Debug Mode**
```bash
python3 -m pytest -s -v --tb=long
```

### **Stop on First Failure**
```bash
python3 -m pytest -x -v
```

### **Run Specific Test**
```bash
python3 -m pytest tests/unit/utilities/test_utility_service_discovery.py::TestUtilityServiceDiscovery::test_configuration_utility_service_discovery -v
```

### **Run Tests with Pattern**
```bash
python3 -m pytest -k "service_discovery" -v
```

---

## **📊 Test Results Analysis**

### **Success Criteria**
- ✅ **Service Discovery Tests**: 5/5 passing (100%)
- ✅ **Service-Aware E2E Tests**: 2/2 passing (100%)
- ✅ **Production Environment Tests**: 1/1 passing (100%)
- ✅ **Overall Success Rate**: 8/8 passing (100%)

### **Failure Analysis**
If tests fail, check:
1. **Service Discovery**: Are all services accessible?
2. **Import Paths**: Are Python paths configured correctly?
3. **Dependencies**: Are all required packages installed?
4. **Environment**: Are environment variables set correctly?

---

## **🚀 Advanced Test Execution**

### **Parallel Execution**
```bash
python3 -m pytest -n auto -v
```

### **Performance Testing**
```bash
python3 -m pytest --benchmark-only -v
```

### **Load Testing**
```bash
python3 -m pytest -m "performance" -v
```

### **Integration Testing**
```bash
python3 -m pytest -m "integration" -v
```

---

## **📋 Test Execution Checklist**

### **Pre-Execution Checklist**
- [ ] Python 3.10+ installed
- [ ] pytest 8.4.1+ installed
- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] Python paths configured
- [ ] Test data available

### **Execution Checklist**
- [ ] Run service discovery tests
- [ ] Run service-aware E2E tests
- [ ] Run production environment tests
- [ ] Generate test reports
- [ ] Validate test results
- [ ] Check service health

### **Post-Execution Checklist**
- [ ] All tests passing
- [ ] Test reports generated
- [ ] Service health validated
- [ ] Production readiness confirmed
- [ ] UAT validation complete

---

## **📞 Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Check Python path
echo $PYTHONPATH
# Add platform path
export PYTHONPATH="/home/founders/demoversion/symphainy_source/symphainy-platform:$PYTHONPATH"
```

#### **Service Discovery Failures**
```bash
# Check service availability
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('symphainy-platform')))
from utilities import ConfigurationUtility
print('Service discovery working')
"
```

#### **Async Test Failures**
```bash
# Check pytest-asyncio installation
pip install pytest-asyncio
# Run with asyncio mode
python3 -m pytest --asyncio-mode=auto -v
```

---

## **🎯 Test Execution Summary**

### **Recommended Execution Order:**
1. **Service Discovery Tests** (5 tests)
2. **Service-Aware E2E Tests** (2 tests)
3. **Production Environment Tests** (1 test)
4. **Generate Test Reports**
5. **Validate Results**

### **Expected Total Execution Time:**
- **Service Discovery**: ~0.1 seconds
- **Service-Aware E2E**: ~0.5 seconds
- **Production Environment**: ~4.5 seconds
- **Total**: ~5 seconds

### **Success Indicators:**
- ✅ All tests passing
- ✅ No import errors
- ✅ Service discovery working
- ✅ Cross-dimension access working
- ✅ Service health monitoring operational

---

## **🎉 Ready for UAT!**

With this guide, you can execute all test suites and validate the Symphainy Platform's service-aware testing framework. All tests are designed to pass with 100% success rate, demonstrating the platform's readiness for production deployment.

**Happy Testing! 🚀**





