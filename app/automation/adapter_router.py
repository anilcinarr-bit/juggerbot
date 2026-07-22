import logging
from typing import Dict, Any, Callable
from app.adapters.base import BaseAdapter
from app.adapters.hepsiburada_adapter import HepsiburadaAdapter
from app.adapters.trendyol_adapter import TrendyolAdapter
from app.adapters.n11_adapter import N11Adapter

logger = logging.getLogger("automation.adapter_router")

class AdapterRouter:
    """Routes automation execution to appropriate adapters based on platform"""
    
    def __init__(self):
        """Initialize the adapter router with registered adapters"""
        self._adapters: Dict[str, Callable[[], BaseAdapter]] = {}
        self._initialize_adapters()
        
    def _initialize_adapters(self):
        """Register all available adapters"""
        self.register("hepsiburada", HepsiburadaAdapter)
        self.register("trendyol", TrendyolAdapter)
        self.register("n11", N11Adapter)
        
    def register(self, platform: str, adapter_class: Callable[[], BaseAdapter]):
        """
        Register an adapter for a specific platform
        
        Args:
            platform: The platform name (e.g., "hepsiburada", "trendyol")
            adapter_class: The adapter class to register
        """
        logger.info(f"Registering adapter for platform: {platform}")
        self._adapters[platform] = adapter_class
        
    def get_adapter(self, platform: str) -> BaseAdapter:
        """
        Get the appropriate adapter for a platform
        
        Args:
            platform: The platform name
            
        Returns:
            The adapter instance for the platform
            
        Raises:
            ValueError: If no adapter is registered for the platform
        """
        if platform not in self._adapters:
            raise ValueError(f"No adapter registered for platform: {platform}")
            
        adapter_class = self._adapters[platform]
        return adapter_class()
        
    async def execute(self, platform: str, coupon: str) -> Dict[str, Any]:
        """
        Execute the appropriate adapter for the given platform
        
        Args:
            platform: The platform name
            coupon: The coupon code to process
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing automation for platform: {platform}")
        logger.info(f"Selected adapter: {platform}Adapter")
        
        try:
            # Get the appropriate adapter
            adapter = self.get_adapter(platform)
            
            # Execute the adapter and return results
            result = await adapter.execute(coupon)
            
            logger.info(f"Automation execution completed for platform: {platform}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing automation for platform {platform}: {e}")
            raise

# Create a singleton instance to match the import pattern used elsewhere in the project
adapter_router = AdapterRouter()
