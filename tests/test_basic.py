"""
Basic smoke tests to verify package structure and imports.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all main modules can be imported."""
    try:
        from golf_assistant import QwenVLAgent, WebScraper, SatelliteRetriever
        from golf_assistant.schemas import (
            GolfCourseInfo,
            VegetationAnalysis,
            GolfCourseAnalysisResult,
            validate_analysis_output,
            export_json_schema
        )
        from golf_assistant.utils import Config, get_config, setup_logging
        
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_instantiation():
    """Test that classes can be instantiated."""
    try:
        from golf_assistant import QwenVLAgent, WebScraper, SatelliteRetriever
        
        # Test WebScraper
        scraper = WebScraper()
        assert scraper is not None
        print("✓ WebScraper instantiated")
        
        # Test SatelliteRetriever
        retriever = SatelliteRetriever()
        assert retriever is not None
        print("✓ SatelliteRetriever instantiated")
        
        # Test QwenVLAgent (without loading model)
        agent = QwenVLAgent(load_model=False)
        assert agent is not None
        print("✓ QwenVLAgent instantiated")
        
        return True
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_validation():
    """Test schema validation."""
    try:
        from golf_assistant.schemas import (
            GolfCourseInfo,
            GolfCourseAnalysisResult,
            validate_analysis_output
        )
        from datetime import datetime
        
        # Test schema creation
        course = GolfCourseInfo(
            name="Test Course",
            holes=18,
            par=72
        )
        assert course.name == "Test Course"
        print("✓ GolfCourseInfo schema works")
        
        # Test analysis result validation
        analysis_data = {
            'timestamp': datetime.now(),
            'course_info': {
                'name': 'Test Course',
                'holes': 18,
                'par': 72
            },
            'recommendations': [],
            'insights': []
        }
        
        result = validate_analysis_output(analysis_data)
        assert result is not None
        print("✓ Schema validation works")
        
        return True
    except Exception as e:
        print(f"✗ Schema validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration system."""
    try:
        from golf_assistant.utils import Config, get_config
        
        # Test default config
        config = Config()
        assert config is not None
        
        # Test getting values
        timeout = config.get('scraper.timeout', 30)
        assert timeout == 30
        print("✓ Configuration system works")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ndvi_calculation():
    """Test NDVI calculation."""
    try:
        import numpy as np
        from golf_assistant import SatelliteRetriever
        
        retriever = SatelliteRetriever()
        
        # Create test data
        red = np.array([[100, 150], [200, 250]], dtype=np.float32)
        nir = np.array([[150, 200], [250, 300]], dtype=np.float32)
        
        # Calculate NDVI
        ndvi = retriever.calculate_ndvi(red, nir)
        
        # Verify output shape
        assert ndvi.shape == red.shape
        
        # Verify NDVI values are in valid range
        assert np.all(ndvi >= -1) and np.all(ndvi <= 1)
        
        print("✓ NDVI calculation works")
        return True
    except Exception as e:
        print(f"✗ NDVI calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Golf Course Assistant Tests")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Instantiation Test", test_basic_instantiation),
        ("Schema Validation Test", test_schema_validation),
        ("Configuration Test", test_config),
        ("NDVI Calculation Test", test_ndvi_calculation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(result for _, result in results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
