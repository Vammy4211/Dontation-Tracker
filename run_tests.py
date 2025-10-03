"""
Test runner script for the donation tracker application.

This script provides various testing options including running specific test suites,
generating coverage reports, and running performance tests.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, capture_output=False):
    """Run a command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return False, "", str(e)


def install_test_dependencies():
    """Install testing dependencies."""
    print("Installing testing dependencies...")
    
    dependencies = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "pytest-asyncio>=0.21.0",
        "pytest-xdist>=3.0.0",
        "coverage>=7.0.0"
    ]
    
    for dep in dependencies:
        success, stdout, stderr = run_command(f"pip install {dep}")
        if not success:
            print(f"Failed to install {dep}: {stderr}")
            return False
        print(f"✓ Installed {dep}")
    
    return True


def run_unit_tests(pattern=None, verbose=False):
    """Run unit tests."""
    print("Running unit tests...")
    
    cmd = "pytest tests/ -m unit"
    if pattern:
        cmd += f" -k {pattern}"
    if verbose:
        cmd += " -v"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✓ Unit tests passed!")
    else:
        print(f"✗ Unit tests failed: {stderr}")
    
    return success


def run_pattern_tests(verbose=False):
    """Run design pattern tests."""
    print("Running design pattern tests...")
    
    pattern_files = [
        "test_factory_pattern.py",
        "test_singleton_pattern.py", 
        "test_repository_pattern.py",
        "test_strategy_pattern.py"
    ]
    
    all_passed = True
    
    for pattern_file in pattern_files:
        print(f"\n📋 Testing {pattern_file.replace('test_', '').replace('_pattern.py', '')} pattern...")
        
        cmd = f"pytest tests/{pattern_file}"
        if verbose:
            cmd += " -v"
        
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✓ {pattern_file} tests passed!")
        else:
            print(f"✗ {pattern_file} tests failed: {stderr}")
            all_passed = False
    
    return all_passed


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("Running integration tests...")
    
    cmd = "pytest tests/ -m integration"
    if verbose:
        cmd += " -v"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✓ Integration tests passed!")
    else:
        print(f"✗ Integration tests failed: {stderr}")
    
    return success


def run_all_tests(verbose=False):
    """Run all tests."""
    print("Running all tests...")
    
    cmd = "pytest tests/"
    if verbose:
        cmd += " -v"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✓ All tests passed!")
    else:
        print(f"✗ Some tests failed: {stderr}")
    
    return success


def generate_coverage_report():
    """Generate test coverage report."""
    print("Generating coverage report...")
    
    # Run tests with coverage
    cmd = "pytest tests/ --cov=app --cov-report=html --cov-report=term-missing"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✓ Coverage report generated!")
        print("📊 HTML report available at: htmlcov/index.html")
        
        # Try to open coverage report
        coverage_file = Path("htmlcov/index.html")
        if coverage_file.exists():
            print(f"📂 Coverage report path: {coverage_file.absolute()}")
    else:
        print(f"✗ Failed to generate coverage report: {stderr}")
    
    return success


def run_performance_tests(verbose=False):
    """Run performance tests."""
    print("Running performance tests...")
    
    cmd = "pytest tests/ -m slow"
    if verbose:
        cmd += " -v"
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✓ Performance tests passed!")
    else:
        print(f"✗ Performance tests failed: {stderr}")
    
    return success


def lint_code():
    """Run code linting."""
    print("Running code linting...")
    
    # Try to install flake8 if not available
    run_command("pip install flake8", capture_output=True)
    
    cmd = "flake8 app/ tests/ --max-line-length=100 --ignore=E501,W503"
    success, stdout, stderr = run_command(cmd, capture_output=True)
    
    if success:
        print("✓ Code linting passed!")
    else:
        print(f"⚠️  Linting issues found:\n{stdout}")
    
    return success


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Donation Tracker Test Runner")
    parser.add_argument("--install-deps", action="store_true", 
                       help="Install testing dependencies")
    parser.add_argument("--unit", action="store_true", 
                       help="Run unit tests only")
    parser.add_argument("--patterns", action="store_true", 
                       help="Run design pattern tests only")
    parser.add_argument("--integration", action="store_true", 
                       help="Run integration tests only")
    parser.add_argument("--all", action="store_true", 
                       help="Run all tests")
    parser.add_argument("--coverage", action="store_true", 
                       help="Generate coverage report")
    parser.add_argument("--performance", action="store_true", 
                       help="Run performance tests")
    parser.add_argument("--lint", action="store_true", 
                       help="Run code linting")
    parser.add_argument("--pattern", type=str, 
                       help="Run tests matching pattern")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Donation Tracker Test Runner")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)
        print()
    
    success = True
    
    # Run requested tests
    if args.unit:
        success &= run_unit_tests(args.pattern, args.verbose)
    elif args.patterns:
        success &= run_pattern_tests(args.verbose)
    elif args.integration:
        success &= run_integration_tests(args.verbose)
    elif args.all:
        success &= run_all_tests(args.verbose)
    elif args.coverage:
        success &= generate_coverage_report()
    elif args.performance:
        success &= run_performance_tests(args.verbose)
    elif args.lint:
        success &= lint_code()
    else:
        # Default: run pattern tests (most important for demonstration)
        print("No specific test type specified. Running design pattern tests...")
        success &= run_pattern_tests(args.verbose)
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 All tests completed successfully!")
        print("\n📋 Available test commands:")
        print("  python run_tests.py --patterns     # Test design patterns")
        print("  python run_tests.py --all          # Run all tests")
        print("  python run_tests.py --coverage     # Generate coverage report")
        print("  python run_tests.py --lint         # Run code linting")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()