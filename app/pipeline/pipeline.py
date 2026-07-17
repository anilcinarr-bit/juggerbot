from typing import List
from app.models.incoming_message import IncomingMessage
from app.pipeline.steps import logger_step, forward_engine_step


class Pipeline:
    """Pipeline for processing incoming messages"""
    
    def __init__(self, steps: List[callable]):
        self.steps = steps
    
    async def process(self, message: IncomingMessage) -> None:
        """Process the message through all pipeline steps"""
        for step in self.steps:
            await step(message)
