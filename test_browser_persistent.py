import asyncio
from app.browser.browser_manager import BrowserManager

async def test_browser_persistent():
    """Test that the browser manager works with persistent contexts"""
    
    # Get the browser manager instance
    browser_manager = BrowserManager()
    
    try:
        # Start the browser manager (this should work even on Windows)
        await browser_manager.start()
        
        print("Browser manager started successfully")
        print(f"Browser available: {browser_manager.available}")
        
        if browser_manager.available:
            # Test getting context
            context = browser_manager.context
            print(f"Context available: {context is not None}")
            
            # Test creating a new page from persistent context
            page = await browser_manager.new_page()
            print(f"New page created successfully: {page is not None}")
            
            # Test that we can get the same context multiple times
            context2 = await browser_manager.get_context_for_platform("test")
            print(f"Same context returned: {context is context2}")
            
        # Stop the browser manager
        await browser_manager.stop()
        print("Browser manager stopped successfully")
        
    except Exception as e:
        print(f"Error in test: {e}")
        # Even if there's an error, we should still try to stop
        try:
            await browser_manager.stop()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_browser_persistent())