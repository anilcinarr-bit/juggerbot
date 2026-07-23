import asyncio
import sys
from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

browser = None

@app.on_event("startup")
async def startup_event():
    global browser
    
    # Set the correct event loop policy for Windows BEFORE any other imports
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            print("WindowsProactorEventLoopPolicy set successfully")
        except NotImplementedError:
            pass

    print("Starting Playwright...")
    try:
        playwright = await async_playwright().start()
        print("Playwright started successfully")
        
        browser = await playwright.chromium.launch(headless=False)
        print("Browser launched successfully")
        
        page = await browser.new_page()
        print("Page created successfully")
        
        await page.goto("https://example.com")
        print("Navigated to example.com successfully")
        
        # Keep the page open for a moment
        await asyncio.sleep(2)
        
        print("Reproduction test completed successfully")
        
    except Exception as e:
        print(f"Error during reproduction test: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    global browser
    if browser:
        await browser.close()
        print("Browser closed")

@app.get("/")
async def root():
    return {"message": "Playwright FastAPI reproduction test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)