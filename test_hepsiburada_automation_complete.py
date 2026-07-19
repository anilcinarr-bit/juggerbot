#!/usr/bin/env python3
"""
Test script for complete Hepsiburada automation flow.
This will run the full integration test to demonstrate the automation working end-to-end.
"""

import asyncio
import logging
from app.adapters.hepsiburada_adapter import HepsiburadaAdapter

# Configure logging to see the automation process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_hepsiburada_automation():
    """Test the complete Hepsiburada automation flow"""
    print("Testing complete Hepsiburada automation flow...")
    
    # Create adapter instance
    adapter = HepsiburadaAdapter()
    
    # Test with a sample coupon code
    test_coupon = "HEPSI-500"
    
    try:
        # Execute the automation
        result = await adapter.execute(coupon=test_coupon)
        print(f"Automation completed with result: {result}")
        return result
    except Exception as e:
        print(f"Error during automation: {e}")
        raise

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_hepsiburada_automation())