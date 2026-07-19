import logging
from typing import Any, Dict
from app.models.incoming_message import IncomingMessage

logger = logging.getLogger("adapters.base")


class BaseAdapter:
    """Base adapter class for implementing different service adapters"""
    
    async def execute(self, message: IncomingMessage) -> Dict[str, Any]:
        """
        Execute the adapter logic
        
        Args:
            message: The IncomingMessage to process
            
        Returns:
            Dict containing execution results and metadata
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement execute() method")