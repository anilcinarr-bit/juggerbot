import asyncio
from app.models.incoming_message import IncomingMessage
from app.automation.engine import AutomationEngine

# Since we can't actually send Telegram messages in this environment,
# let's simulate what would happen when processing the real messages

async def test_real_messages():
    """Test processing of actual messages that would come from Telegram"""
    
    # Create automation engine
    engine = AutomationEngine()
    
    print("Testing real message processing...")
    print("=" * 60)
    
    # These are the exact messages from the requirement
    test_messages = [
        {
            "text": "Hepsiburada mutfak alışverişinde geçerli\nHEPSI-500",
            "description": "Hepsiburada message with coupon"
        },
        {
            "text": "N11 kuponu\nGECE500", 
            "description": "N11 message with coupon"
        },
        {
            "text": "Trendyol kodu\nTREND250",
            "description": "Trendyol message with coupon"
        }
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n--- Message {i}: {test['description']} ---")
        print(f"Text: {test['text']}")
        
        # Create a mock IncomingMessage (we can't use the real one without Telegram connection)
        # But we'll show what would happen in the actual system
        print("Processing through automation engine...")
        print("Expected logs that would appear:")
        print("  Automation trigger received")
        print("  Original message:", test['text'])
        print("  Normalized message: [normalized version]")
        print("  Coupon detected: [coupon code]")
        print("  Detected platform: [platform name]")
        print("  Confidence: [confidence score]")
        print("  Selected adapter: [platform]Adapter")
        print("  Adapter execution started...")
        
        # Show what the platform detector would find
        from app.automation.platform_detector import PlatformDetector
        detector = PlatformDetector()
        result = detector.detect_platform(test['text'], "COUPON_CODE")
        print(f"  Detected platform: {result.platform}")
        print(f"  Confidence: {result.confidence:.2f}")
        
        print("  Adapter execution completed")

if __name__ == "__main__":
    asyncio.run(test_real_messages())