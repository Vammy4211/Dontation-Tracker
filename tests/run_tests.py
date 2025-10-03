# Simple test runner for our donation tracker
import unittest
import sys
import os

# Add app to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == '__main__':
    # Find and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Simple summary
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Some tests failed: {len(result.failures)} failures, {len(result.errors)} errors")