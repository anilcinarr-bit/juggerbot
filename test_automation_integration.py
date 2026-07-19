#!/usr/bin/env python3
"""Test script for AutomationEngine integration with CouponExtractor."""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.automation.engine import AutomationEngine
from app.models.incoming_message import IncomingMessage
import datetime as dt

async def test_automation_engine_integration():
    """Test the AutomationEngine with CouponExtractor integration."""
    
    engine = AutomationEngine()
    
    # Create a mock message
    mock_message = IncomingMessage(
        message_id=12345,
        chat_id=98765,
        chat_title="Test Chat",
        sender_id=54321,
        sender_name="Test User",
        text="Use code SAVE50 for 50% off or WELCOME2026 for new users",
        date=dt.datetime.now(),
        has_media=False,
        raw_event=None
    )
    
    print("Testing AutomationEngine with coupon extraction...")
    
    # Test case 1: Message with coupons
    print("\n=== Test Case 1: Message with coupons ===")
    result = await engine.execute(mock_message)
    print(f"Result status: {result.get('status')}")
    print(f"Detected coupons: {result.get('detected_coupons', [])}")
    
    # Create another mock message without coupons
    mock_message_no_coupons = IncomingMessage(
        message_id=12346,
        chat_id=98766,
        chat_title="Test Chat 2",
        sender_id=54322,
        sender_name="Another User",
        text="This is a regular message without any coupons",
        date=dt.datetime.now(),
        has_media=False,
        raw_event=None
    )
    
    print("\n=== Test Case 2: Message without coupons ===")
    result_no_coupons = await engine.execute(mock_message_no_coupons)
    print(f"Result status: {result_no_coupons.get('status')}")
    print(f"Detected coupons: {result_no_coupons.get('detected_coupons', [])}")
    
    print("\n🎉 Integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_automation_engine_integration())
