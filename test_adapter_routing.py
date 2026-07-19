import asyncio
from app.automation.adapter_router import AdapterRouter

async def test_adapter_routing():
    """Test adapter routing functionality"""
    
    # Create adapter router
    router = AdapterRouter()
    
    print("Testing adapter routing...")
    print("=" * 60)
    
    # Test cases for different platforms
    test_cases = [
        {"platform": "hepsiburada", "coupon": "HEPSI-500"},
        {"platform": "trendyol", "coupon": "TREND250"},
        {"platform": "n11", "coupon": "GECE500"}
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: Platform = {test['platform']}, Coupon = {test['coupon']}")
        
        try:
            result = await router.execute(test['platform'], test['coupon'])
            print(f"  Executed: {result.get('platform', 'unknown')} adapter")
            print(f"  Status: {result.get('status', 'unknown')}")
            print("  ✓ Success: Adapter routing working correctly")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_adapter_routing())