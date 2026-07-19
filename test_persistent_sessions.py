#!/usr/bin/env python3
"""
Test script for persistent browser sessions functionality.
This will test that the BrowserManager properly handles persistent contexts 
for different platforms.
"""

import asyncio
import logging
from app.browser.browser_manager import BrowserManager

# Configure logging to see the automation process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_persistent_sessions():
    """Test the persistent browser session functionality"""
    print("Testing persistent browser sessions...")
    
    # Create browser manager instance
    browser_manager = BrowserManager()
    
    try:
        # Start the browser manager
        await browser_manager.start()
        print("✓ Browser manager started successfully")
        
        # Test getting contexts for different platforms
        hepsiburada_context = await browser_manager.get_context_for_platform("hepsiburada")
        print("✓ Hepsiburada context created successfully")
        
        trendyol_context = await browser_manager.get_context_for_platform("trendyol")
        print("✓ Trendyol context created successfully")
        
        n11_context = await browser_manager.get_context_for_platform("n11")
        print("✓ N11 context created successfully")
        
        # Test login status checking
        is_logged_in_hepsiburada = await browser_manager.is_logged_in("hepsiburada")
        print(f"✓ Hepsiburada login status check: {is_logged_in_hepsiburada}")
        
        # Test getting current URL (should be blank initially)
        current_url = await browser_manager.current_url()
        print(f"✓ Current URL: {current_url}")
        
        # Test getting current title (should be blank initially)
        current_title = await browser_manager.current_title()
        print(f"✓ Current title: {current_title}")
        
        # Save storage state
        await browser_manager.save_storage_state()
        print("✓ Storage state saved successfully")
        
        # Stop the browser manager
        await browser_manager.stop()
        print("✓ Browser manager stopped successfully")
        
        print("\n✓ All persistent session tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_persistent_sessions())
    if result:
        print("\n🎉 Persistent sessions functionality working correctly!")
    else:
        print("\n❌ Persistent sessions functionality has issues!")