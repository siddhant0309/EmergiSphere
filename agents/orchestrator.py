"""
MediSentinel Agent Orchestrator

This module coordinates all AI agents in the MediSentinel system, managing
workflow execution, agent communication, and error handling.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage
from crewai import Crew, Process

from .triage_agent import TriageAgent
from .admission_agent import AdmissionAgent
from .billing_agent import BillingAgent
from .legal_agent import LegalAgent
from .scheduling_agent import SchedulingAgent
from .medical_records_agent import MedicalRecordsAgent
from .communication_agent import CommunicationAgent
from .smart_health_device_agent import SmartHealthDeviceAgent

logger = logging.getLogger(__name__)


class WorkflowContext(BaseModel):
    """Context for workflow execution across agents."""
    session_id: str
    patient_id: Optional[str] = None
    emergency_level: Optional[str] = None
    legal_case: Optional[bool] = None
    workflow_type: str  # "emergency" or "regular"
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentOrchestrator:
    """
    Central coordinator for all MediSentinel AI agents.
    
    Manages agent interactions, workflow execution, and ensures
    compliance with hospital protocols.
    """
    
    def __init__(self):
        self.agents = {
            'triage': TriageAgent(),
            'admission': AdmissionAgent(),
            'billing': BillingAgent(),
            'legal': LegalAgent(),
            'scheduling': SchedulingAgent(),
            'medical_records': MedicalRecordsAgent(),
            'communication': CommunicationAgent(),
            'smart_health_device': SmartHealthDeviceAgent()
        }
        
        self.active_sessions: Dict[str, WorkflowContext] = {}
        self.workflow_definitions = self._define_workflows()
    
    def _define_workflows(self) -> Dict[str, List[str]]:
        """Define the sequence of agents for different workflow types."""
        return {
            'emergency': [
                'triage',
                'admission', 
                'legal',
                'medical_records',
                'smart_health_device',
                'billing',
                'communication',
                'scheduling'
            ],
            'regular': [
                'admission',
                'triage',
                'medical_records',
                'smart_health_device',
                'billing',
                'scheduling',
                'communication'
            ],
            'device_scan': [
                'smart_health_device',
                'medical_records',
                'communication'
            ],
            'emergency_device': [
                'smart_health_device',
                'triage',
                'communication',
                'admission'
            ]
        }
    
    async def start_workflow(
        self, 
        workflow_type: str, 
        initial_data: Dict[str, Any]
    ) -> str:
        """
        Start a new workflow session.
        
        Args:
            workflow_type: Type of workflow ('emergency' or 'regular')
            initial_data: Initial data for the workflow
            
        Returns:
            Session ID for tracking the workflow
        """
        session_id = str(uuid4())
        
        context = WorkflowContext(
            session_id=session_id,
            workflow_type=workflow_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=initial_data
        )
        
        self.active_sessions[session_id] = context
        
        logger.info(f"Started {workflow_type} workflow with session {session_id}")
        
        # Start workflow execution asynchronously
        asyncio.create_task(self._execute_workflow(session_id))
        
        return session_id
    
    async def _execute_workflow(self, session_id: str):
        """Execute the workflow for a given session."""
        context = self.active_sessions.get(session_id)
        if not context:
            logger.error(f"Session {session_id} not found")
            return
        
        workflow_sequence = self.workflow_definitions[context.workflow_type]
        
        try:
            for agent_name in workflow_sequence:
                agent = self.agents[agent_name]
                
                logger.info(f"Executing {agent_name} agent for session {session_id}")
                
                # Execute agent with current context
                result = await agent.process(context)
                
                # Update context with agent results
                context.metadata.update(result)
                context.updated_at = datetime.utcnow()
                
                # Update specific context fields based on agent
                await self._update_context_from_agent(context, agent_name, result)
                
                logger.info(f"Completed {agent_name} agent for session {session_id}")
                
        except Exception as e:
            logger.error(f"Error in workflow execution for session {session_id}: {e}")
            await self._handle_workflow_error(session_id, e)
    
    async def _update_context_from_agent(
        self, 
        context: WorkflowContext, 
        agent_name: str, 
        result: Dict[str, Any]
    ):
        """Update workflow context based on agent results."""
        if agent_name == 'triage':
            context.emergency_level = result.get('emergency_level')
        elif agent_name == 'admission':
            context.patient_id = result.get('patient_id')
        elif agent_name == 'legal':
            context.legal_case = result.get('legal_case')
    
    async def _handle_workflow_error(self, session_id: str, error: Exception):
        """Handle errors during workflow execution."""
        context = self.active_sessions.get(session_id)
        if context:
            context.metadata['error'] = str(error)
            context.metadata['error_timestamp'] = datetime.utcnow().isoformat()
            
            # Notify communication agent about the error
            await self.agents['communication'].notify_error(context, error)
    
    async def get_workflow_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow session."""
        context = self.active_sessions.get(session_id)
        if not context:
            return None
        
        return {
            'session_id': context.session_id,
            'workflow_type': context.workflow_type,
            'emergency_level': context.emergency_level,
            'patient_id': context.patient_id,
            'legal_case': context.legal_case,
            'created_at': context.created_at.isoformat(),
            'updated_at': context.updated_at.isoformat(),
            'status': 'active' if context.session_id in self.active_sessions else 'completed'
        }
    
    async def complete_workflow(self, session_id: str):
        """Mark a workflow as completed and clean up resources."""
        if session_id in self.active_sessions:
            context = self.active_sessions.pop(session_id)
            logger.info(f"Completed workflow session {session_id}")
            
            # Store workflow results for audit purposes
            await self._store_workflow_results(context)
    
    async def _store_workflow_results(self, context: WorkflowContext):
        """Store workflow results for audit and compliance purposes."""
        # This would typically store to a database
        logger.info(f"Storing workflow results for session {context.session_id}")
    
    async def emergency_override(self, session_id: str, override_data: Dict[str, Any]):
        """
        Handle emergency overrides when immediate action is required.
        
        This bypasses normal workflow sequence for critical situations.
        """
        context = self.active_sessions.get(session_id)
        if not context:
            raise ValueError(f"Session {session_id} not found")
        
        # Immediately execute critical agents
        critical_agents = ['triage', 'admission', 'communication']
        
        for agent_name in critical_agents:
            agent = self.agents[agent_name]
            await agent.emergency_process(context, override_data)
    
    async def get_agent_health(self) -> Dict[str, bool]:
        """Check health status of all agents."""
        health_status = {}
        
        for agent_name, agent in self.agents.items():
            try:
                health_status[agent_name] = await agent.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {agent_name}: {e}")
                health_status[agent_name] = False
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator and all agents."""
        logger.info("Shutting down Agent Orchestrator")
        
        # Complete all active workflows
        for session_id in list(self.active_sessions.keys()):
            await self.complete_workflow(session_id)
        
        # Shutdown all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.info(f"Shutdown {agent_name} agent")
            except Exception as e:
                logger.error(f"Error shutting down {agent_name} agent: {e}")


# Global orchestrator instance
orchestrator = AgentOrchestrator()


async def get_orchestrator() -> AgentOrchestrator:
    """Dependency injection for FastAPI."""
    return orchestrator 