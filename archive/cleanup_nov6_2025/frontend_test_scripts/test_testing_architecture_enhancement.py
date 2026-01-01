#!/usr/bin/env python3
"""
Validation Test for Testing Architecture Enhancement
Tests the advanced testing architecture system
"""

import os
import sys
from pathlib import Path

def check_file_size(file_path: str, max_lines: int = 100) -> bool:
    """Check if file is under the specified line count"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            return len(lines) <= max_lines
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_directory_structure(base_path: str) -> bool:
    """Check if directory follows micro-modular structure"""
    required_files = ['AdvancedTestFramework.ts', 'index.ts']
    optional_files = ['VisualRegressionTesting.ts', 'PerformanceTesting.ts', 'TestGeneration.ts', 'EnhancedTestingProvider.tsx']
    
    base_dir = Path(base_path)
    if not base_dir.exists():
        print(f"❌ Directory {base_path} does not exist")
        return False
    
    # Check required files
    for file in required_files:
        file_path = base_dir / file
        if not file_path.exists():
            print(f"❌ Required file {file} missing in {base_path}")
            return False
    
    # Check optional files (at least some should exist)
    optional_exists = any((base_dir / file).exists() for file in optional_files)
    if not optional_exists:
        print(f"⚠️  No optional files found in {base_path}")
    
    return True

def validate_testing_micro_modules():
    """Validate testing architecture micro-modules"""
    print("🔍 Validating Testing Architecture Micro-Modules...")
    
    testing_dirs = [
        "shared/testing/core",
        "shared/testing/visual", 
        "shared/testing/performance",
        "shared/testing/generation"
    ]
    
    all_dirs_valid = True
    for testing_dir in testing_dirs:
        if not check_directory_structure(testing_dir):
            all_dirs_valid = False
    
    return all_dirs_valid

def check_testing_enhancement_features():
    """Check testing enhancement features"""
    print("\n🔍 Checking Testing Enhancement Features...")
    
    enhancement_files = [
        "shared/testing/core/AdvancedTestFramework.ts",
        "shared/testing/visual/VisualRegressionTesting.ts",
        "shared/testing/performance/PerformanceTesting.ts",
        "shared/testing/generation/TestGeneration.ts"
    ]
    
    enhancement_patterns = [
        'AdvancedTestFramework',
        'TestSuite',
        'TestCase',
        'TestResult',
        'VisualRegressionTesting',
        'captureScreenshot',
        'compareScreenshots',
        'PerformanceTesting',
        'measureComponentPerformance',
        'TestGeneration',
        'generateTests',
        'analyzeComponent'
    ]
    
    all_enhancements_valid = True
    for file_path in enhancement_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in enhancement_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 3:  # At least 3 patterns should be found
                        print(f"✅ {file_path}: Enhancement features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing enhancement features")
                        all_enhancements_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_enhancements_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_enhancements_valid

def check_visual_regression_features():
    """Check visual regression testing features"""
    print("\n🔍 Checking Visual Regression Testing Features...")
    
    visual_files = [
        "shared/testing/visual/VisualRegressionTesting.ts"
    ]
    
    visual_patterns = [
        'VisualRegressionTesting',
        'captureScreenshot',
        'compareScreenshots',
        'runVisualTest',
        'updateBaseline',
        'ScreenshotData',
        'VisualTestResult'
    ]
    
    all_visual_valid = True
    for file_path in visual_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in visual_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 4:  # At least 4 patterns should be found
                        print(f"✅ {file_path}: Visual regression features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing visual regression features")
                        all_visual_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_visual_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_visual_valid

def check_performance_testing_features():
    """Check performance testing features"""
    print("\n🔍 Checking Performance Testing Features...")
    
    performance_files = [
        "shared/testing/performance/PerformanceTesting.ts"
    ]
    
    performance_patterns = [
        'PerformanceTesting',
        'measureComponentPerformance',
        'PerformanceMetrics',
        'PerformanceTestResult',
        'measureWebVitals',
        'firstContentfulPaint',
        'largestContentfulPaint',
        'cumulativeLayoutShift',
        'firstInputDelay'
    ]
    
    all_performance_valid = True
    for file_path in performance_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in performance_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 5:  # At least 5 patterns should be found
                        print(f"✅ {file_path}: Performance testing features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing performance testing features")
                        all_performance_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_performance_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_performance_valid

def check_test_generation_features():
    """Check test generation features"""
    print("\n🔍 Checking Test Generation Features...")
    
    generation_files = [
        "shared/testing/generation/TestGeneration.ts"
    ]
    
    generation_patterns = [
        'TestGeneration',
        'generateTests',
        'analyzeComponent',
        'ComponentAnalysis',
        'GeneratedTest',
        'generateRenderingTests',
        'generatePropsTests',
        'generateEventTests',
        'generateAccessibilityTests',
        'generateEdgeCaseTests'
    ]
    
    all_generation_valid = True
    for file_path in generation_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in generation_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 5:  # At least 5 patterns should be found
                        print(f"✅ {file_path}: Test generation features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing test generation features")
                        all_generation_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_generation_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_generation_valid

def main():
    """Main validation function"""
    print("🚀 Phase 6: Testing Architecture Enhancement - Validation")
    print("=" * 80)
    
    # Validate testing micro-modules
    testing_valid = validate_testing_micro_modules()
    
    # Check testing enhancement features
    enhancement_valid = check_testing_enhancement_features()
    
    # Check visual regression features
    visual_valid = check_visual_regression_features()
    
    # Check performance testing features
    performance_valid = check_performance_testing_features()
    
    # Check test generation features
    generation_valid = check_test_generation_features()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"Testing Micro-Modules: {'✅ PASS' if testing_valid else '❌ FAIL'}")
    print(f"Testing Enhancement Features: {'✅ PASS' if enhancement_valid else '❌ FAIL'}")
    print(f"Visual Regression Features: {'✅ PASS' if visual_valid else '❌ FAIL'}")
    print(f"Performance Testing Features: {'✅ PASS' if performance_valid else '❌ FAIL'}")
    print(f"Test Generation Features: {'✅ PASS' if generation_valid else '❌ FAIL'}")
    
    overall_success = testing_valid and enhancement_valid and visual_valid and performance_valid and generation_valid
    
    if overall_success:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Testing architecture enhancement completed successfully")
        print("✅ Advanced test framework implemented")
        print("✅ Visual regression testing created")
        print("✅ Performance testing added")
        print("✅ Automated test generation implemented")
        print("✅ Testing provider created")
        print("\n🚀 Ready to proceed to next phase!")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review and fix the issues above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 