#!/usr/bin/env python
"""Run all headless tests."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Run all headless tests."""
    print("="*60)
    print("RUNNING ALL HEADLESS TESTS")
    print("="*60)
    
    tests = [
        ("Models", "test_headless_models"),
        ("Parser", "test_headless_parser"),
        ("Integration", "test_headless_integration")
    ]
    
    all_passed = True
    
    for name, module_name in tests:
        print(f"\n{'='*60}")
        print(f"Running {name} Tests")
        print('='*60)
        
        try:
            module = __import__(module_name)
            if hasattr(module, 'main'):
                result = module.main()
                if not result:
                    all_passed = False
                    print(f"✗ {name} tests failed")
                else:
                    print(f"✓ {name} tests passed")
            else:
                print(f"✗ {name} test module missing main()")
                all_passed = False
        except Exception as e:
            print(f"✗ {name} tests failed with error: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL HEADLESS TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)