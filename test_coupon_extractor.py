#!/usr/bin/env python3
"""Test script for CouponExtractor functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.automation.coupon_extractor import CouponExtractor

def test_coupon_extractor():
    """Test the coupon extractor with various inputs."""
    
    extractor = CouponExtractor()
    
    # Test cases
    test_cases = [
        # (input_text, expected_output)
        ("Use code ABC123 for 20% off", ["ABC123"]),
        ("SAVE50 for 50% discount", ["SAVE50"]),
        ("HEPSI-1234 is your discount code", ["HEPSI-1234"]),
        ("WELCOME2026 for new users", ["WELCOME2026"]),
        ("INDIRIM25 for savings", ["INDIRIM25"]),
        ("ABCD-1234-EFGH promo code", ["ABCD-1234-EFGH"]),
        ("Multiple codes: ABC123 and SAVE50", ["ABC123", "SAVE50"]),
        ("Duplicate codes: ABC123 ABC123", ["ABC123"]),
        ("No coupons here", []),
        ("", []),
        ("Invalid format: 123ABC", []),  # Not matching our patterns
    ]
    
    print("Testing CouponExtractor...")
    all_passed = True
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = extractor.extract(input_text)
        if result == expected:
            print(f"✅ Test {i}: PASSED - '{input_text}' -> {result}")
        else:
            print(f"❌ Test {i}: FAILED - '{input_text}'")
            print(f"   Expected: {expected}")
            print(f"   Got:      {result}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        
    return all_passed

if __name__ == "__main__":
    test_coupon_extractor()