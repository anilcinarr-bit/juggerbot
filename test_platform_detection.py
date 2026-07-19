import asyncio
from app.automation.platform_detector import PlatformDetector

def test_platform_detection():
    """Test platform detection with example messages"""
    
    # Create platform detector
    detector = PlatformDetector()
    
    # Test cases from requirements
    test_cases = [
        {
            "text": "Hepsiburada mutfak alışverişinde geçerli\nHEPSI-500",
            "coupon": "HEPSI-500",
            "expected_platform": "hepsiburada"
        },
        {
            "text": "N11 kuponu:\nGECE500",
            "coupon": "GECE500",
            "expected_platform": "n11"
        },
        {
            "text": "Trendyol kodu:\nTREND250",
            "coupon": "TREND250",
            "expected_platform": "trendyol"
        }
    ]
    
    print("Testing platform detection...")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['text']}")
        print(f"  Coupon: {test['coupon']}")
        
        try:
            result = detector.detect_platform(test['text'], test['coupon'])
            print(f"  Detected platform: {result.platform}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Expected: {test['expected_platform']}")
            if result.platform == test['expected_platform']:
                print("  ✓ Success: Platform detection working correctly")
            else:
                print("  ✗ Error: Platform detection failed")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_platform_detection()
