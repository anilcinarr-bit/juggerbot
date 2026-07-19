#!/usr/bin/env python3
"""Test script for the new weighted scoring PlatformDetector."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.automation.platform_detector import PlatformDetector

def test_weighted_scoring():
    """Test the new weighted scoring platform detector with all examples."""
    
    detector = PlatformDetector()
    
    print("Testing new weighted scoring PlatformDetector")
    print("=" * 60)
    
    # Test cases from requirements
    test_cases = [
        {
            "text": "Hepsiburada mutfak alışverişinde geçerli\nHEPSI-500",
            "coupon": "HEPSI-500",
            "description": "Hepsiburada message with coupon prefix"
        },
        {
            "text": "N11 kuponu\nGECE500", 
            "coupon": "GECE500",
            "description": "N11 message with coupon prefix"
        },
        {
            "text": "Trendyol kodu\nTREND250",
            "coupon": "TREND250",
            "description": "Trendyol message with coupon prefix"
        },
        {
            "text": "N11 kuponu\nHEPSI-500",
            "coupon": "HEPSI-500",
            "description": "Conflict case: N11 message but HEPSI-500 coupon",
            "expected": "hepsiburada"
        },
        {
            "text": "Hepsiburada\nGECE500",
            "coupon": "GECE500",
            "description": "Conflict case: Hepsiburada mention but GECE500 coupon",
            "expected": "n11"
        },
        {
            "text": "Mutfak ürünlerinde geçerli\nHEPSI-500",
            "coupon": "HEPSI-500",
            "description": "Contextual case with HEPSI-500 coupon",
            "expected": "hepsiburada"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Text: {test['text']}")
        print(f"Coupon: {test['coupon']}")
        
        try:
            result = detector.detect_platform(test['text'], test['coupon'])
            print(f"Detected platform: {result.platform}")
            print(f"Confidence: {result.confidence:.2f}")
            
            if 'expected' in test and test['expected'] != result.platform:
                print(f"Expected: {test['expected']} - ❌ FAILED")
                all_passed = False
            elif 'expected' not in test:
                print("✓ Test completed (no specific expectation)")
            else:
                print("✓ Test passed")
                
            # Show scores for debugging
            print("Scores:")
            for platform, score in result.scores.items():
                if score > 0:
                    print(f"  {platform}: {score:.2f}")
                    
        except Exception as e:
            print(f"Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")
        
    return all_passed

if __name__ == "__main__":
    test_weighted_scoring()