import json
import logging
import os
from typing import List, Optional

from app.models import PipelineConfig

logger = logging.getLogger("pipeline.pipeline_manager")


class PipelineManager:
    """Manages forwarding pipelines loaded from configuration"""
    
    def __init__(self, config_path: str = "config/pipelines.json"):
        self.config_path = config_path
        self.pipelines: List[PipelineConfig] = []
        self._load_pipelines()
    
    def _load_pipelines(self) -> None:
        """Load pipelines from JSON configuration file"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Pipeline configuration file not found: {self.config_path}")
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                pipeline_data = json.load(f)
            
            # Convert data to PipelineConfig objects
            self.pipelines = []
            for item in pipeline_data:
                pipeline_config = PipelineConfig(
                    id=item["id"],
                    name=item["name"],
                    enabled=item["enabled"],
                    source_chat_id=item["source_chat_id"],
                    target_chat_id=item["target_chat_id"]
                )
                self.pipelines.append(pipeline_config)
            
            logger.info(f"Loaded {len(self.pipelines)} pipeline(s)")
            
        except Exception as e:
            logger.error(f"Failed to load pipelines from {self.config_path}: {e}")
            raise
    
    def get_pipeline_by_source(self, source_chat_id: int) -> Optional[PipelineConfig]:
        """Get pipeline by source chat ID"""
        for pipeline in self.pipelines:
            if pipeline.source_chat_id == source_chat_id and pipeline.enabled:
                return pipeline
        return None
    
    def get_enabled_pipelines(self) -> List[PipelineConfig]:
        """Get all enabled pipelines"""
        return [p for p in self.pipelines if p.enabled]
    
    def reload(self) -> None:
        """Reload pipelines from configuration file"""
        logger.info("Reloading pipeline configurations...")
        self._load_pipelines()