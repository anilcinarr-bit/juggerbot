#!/usr/bin/env python3
"""Test script to demonstrate Hepsiburada adapter functionality"""

import asyncio
from app.adapters.hepsiburada_adapter import HepsiburadaAdapter

async def test_hepsiburada_adapter():
    """Test the Hepsiburada adapter directly"""
    
    # Create adapter instance
    adapter = HepsiburadaAdapter()
    
    print("Testing HepsiburadaAdapter execute method...")
    try:
        # This should trigger browser navigation
        result = await adapter.execute()
        print(f"Adapter execution completed successfully: {result}")
    except Exception as e:
        print(f"Adapter execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hepsiburada_adapter())
