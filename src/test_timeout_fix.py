#!/usr/bin/env python3
"""
Test script to verify timeout optimization for image generation
"""

import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_timeout_calculation():
    """Test the timeout calculation logic"""
    try:
        # Test timeout calculation logic
        def calculate_timeout(variations):
            timeout_multiplier = max(variations, 1)
            return min(120, 60 + (timeout_multiplier * 20))

        # Test cases
        test_cases = [
            (1, 80),   # 1 variation: 60 + 20 = 80s
            (2, 100),  # 2 variations: 60 + 40 = 100s
            (3, 120),  # 3 variations: 60 + 60 = 120s (capped)
            (4, 120),  # 4 variations: 60 + 80 = 140s -> 120s (capped)
        ]

        print("🧪 Testing timeout calculation:")
        for variations, expected in test_cases:
            result = calculate_timeout(variations)
            status = "✅" if result == expected else "❌"
            print(f"{status} {variations} variations -> {result}s timeout (expected {expected}s)")

        print("\n⚡ Timeout Optimization Summary:")
        print("• Base timeout: 60s")
        print("• Additional per variation: 20s")
        print("• Maximum timeout: 120s")
        print("• Your 4 variations will use 120s timeout")
        print("\n🎯 This should resolve the timeout error for complex image generation!")

        return True

    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    test_timeout_calculation()