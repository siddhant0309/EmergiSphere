"""
Base Agent Class for MediSentinel

This module provides the base class that all MediSentinel agents inherit from,
defining common functionality and interfaces.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel


class BaseAgent(ABC):
    """
    Base class for all MediSentinel AI agents.
    
    Provides common functionality including:
    - Health checking
    - Error handling
    - Logging
    - Resource management
    """
    
    def __init__(self):
        self.agent_name = self.__class__.__name__
        self.logger = logging.getLogger(f"agent.{self.agent_name.lower()}")
        self.is_healthy = True
        self.last_health_check = datetime.utcnow()
        
        self.logger.info(f"Initialized {self.agent_name}")
    
    @abstractmethod
    async def process(self, context: Any) -> Dict[str, Any]:
        """
        Process the main agent logic.
        
        Args:
            context: Workflow context containing relevant data
            
        Returns:
            Dictionary containing agent results
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check if the agent is healthy and functioning properly.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Basic health check - can be overridden by subclasses
            self.is_healthy = True
            self.last_health_check = datetime.utcnow()
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.is_healthy = False
            return False
    
    async def emergency_process(self, context: Any, override_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle emergency processing when normal workflow is bypassed.
        
        Args:
            context: Workflow context
            override_data: Emergency override data
            
        Returns:
            Emergency processing results
        """
        self.logger.warning(f"Emergency processing activated for {self.agent_name}")
        
        # Default emergency behavior - can be overridden by subclasses
        return {
            'emergency_processed': True,
            'agent': self.agent_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the agent and clean up resources."""
        self.logger.info(f"Shutting down {self.agent_name}")
        
        # Mark as unhealthy during shutdown
        self.is_healthy = False
        
        # Cleanup resources if needed
        await self._cleanup()
    
    async def _cleanup(self):
        """Clean up agent resources. Override in subclasses if needed."""
        pass
    
    def _log_processing_start(self, context: Any):
        """Log the start of agent processing."""
        self.logger.info(f"Starting {self.agent_name} processing for session {getattr(context, 'session_id', 'unknown')}")
    
    def _log_processing_complete(self, context: Any, result: Dict[str, Any]):
        """Log the completion of agent processing."""
        self.logger.info(f"Completed {self.agent_name} processing for session {getattr(context, 'session_id', 'unknown')}")
    
    def _log_error(self, context: Any, error: Exception):
        """Log agent processing errors."""
        session_id = getattr(context, 'session_id', 'unknown')
        self.logger.error(f"Error in {self.agent_name} processing for session {session_id}: {error}")
    
    async def _safe_process(self, context: Any) -> Dict[str, Any]:
        """
        Safely execute agent processing with error handling and logging.
        
        Args:
            context: Workflow context
            
        Returns:
            Processing results or error information
        """
        try:
            self._log_processing_start(context)
            
            # Execute the main processing logic
            result = await self.process(context)
            
            self._log_processing_complete(context, result)
            return result
            
        except Exception as e:
            self._log_error(context, e)
            
            # Return error information
            return {
                'error': True,
                'error_message': str(e),
                'agent': self.agent_name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            'agent_name': self.agent_name,
            'is_healthy': self.is_healthy,
            'last_health_check': self.last_health_check.isoformat(),
            'status': 'active' if self.is_healthy else 'unhealthy'
        }
    
    async def validate_input(self, context: Any) -> bool:
        """
        Validate input data for the agent.
        
        Args:
            context: Workflow context to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        # Basic validation - can be overridden by subclasses
        if not context:
            self.logger.error("Context is required")
            return False
        
        return True
    
    async def preprocess(self, context: Any) -> Any:
        """
        Preprocess input data before main processing.
        
        Args:
            context: Workflow context
            
        Returns:
            Preprocessed context
        """
        # Default preprocessing - can be overridden by subclasses
        return context
    
    async def postprocess(self, context: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess results after main processing.
        
        Args:
            context: Workflow context
            result: Processing results
            
        Returns:
            Postprocessed results
        """
        # Default postprocessing - can be overridden by subclasses
        return result 