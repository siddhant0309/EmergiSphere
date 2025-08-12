"""
EmergiSphere Main Application

FastAPI application for the EmergiSphere hospital automation system.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from agents.orchestrator import get_orchestrator, AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models
class EmergencyInput(BaseModel):
    """Input model for emergency cases."""
    voice_input: str = None
    text_input: str = None
    vital_signs: Dict[str, Any] = None
    visual_data: str = None
    contextual_data: Dict[str, Any] = None

class AppointmentInput(BaseModel):
    """Input model for regular appointments."""
    patient_name: str
    patient_id: str = None
    appointment_type: str
    symptoms: str = None
    insurance_info: Dict[str, Any] = None

class WorkflowStatus(BaseModel):
    """Model for workflow status response."""
    session_id: str
    workflow_type: str
    emergency_level: str = None
    patient_id: str = None
    legal_case: bool = None
    status: str
    created_at: str
    updated_at: str

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting EmergiSphere application...")
    
    # Initialize orchestrator
    orchestrator = await get_orchestrator()
    
    yield
    
    # Shutdown
    logger.info("Shutting down EmergiSphere application...")
    await orchestrator.shutdown()

# Create FastAPI app
app = FastAPI(
    title="EmergiSphere API",
    description="Agentic AI for Emergency-First Hospital Automation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "EmergiSphere",
        "version": "1.0.0"
    }

# Agent health check endpoint
@app.get("/health/agents")
async def agent_health_check(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Check health of all agents."""
    try:
        health_status = await orchestrator.get_agent_health()
        return {
            "status": "healthy" if all(health_status.values()) else "degraded",
            "agents": health_status
        }
    except Exception as e:
        logger.error(f"Error checking agent health: {e}")
        raise HTTPException(status_code=500, detail="Error checking agent health")

# Emergency workflow endpoint
@app.post("/emergency/triage", response_model=Dict[str, Any])
async def emergency_triage(
    emergency_input: EmergencyInput,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Start emergency triage workflow.
    
    This endpoint initiates the emergency workflow for critical patient cases.
    """
    try:
        # Start emergency workflow
        session_id = await orchestrator.start_workflow(
            workflow_type="emergency",
            initial_data=emergency_input.dict()
        )
        
        return {
            "session_id": session_id,
            "workflow_type": "emergency",
            "status": "started",
            "message": "Emergency triage workflow initiated"
        }
        
    except Exception as e:
        logger.error(f"Error starting emergency workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Regular appointment endpoint
@app.post("/appointments/schedule", response_model=Dict[str, Any])
async def schedule_appointment(
    appointment_input: AppointmentInput,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Schedule a regular appointment.
    
    This endpoint initiates the regular appointment workflow.
    """
    try:
        # Start regular workflow
        session_id = await orchestrator.start_workflow(
            workflow_type="regular",
            initial_data=appointment_input.dict()
        )
        
        return {
            "session_id": session_id,
            "workflow_type": "regular",
            "status": "started",
            "message": "Appointment scheduling workflow initiated"
        }
        
    except Exception as e:
        logger.error(f"Error starting appointment workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow status endpoint
@app.get("/workflow/{session_id}", response_model=WorkflowStatus)
async def get_workflow_status(
    session_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get the status of a workflow session.
    
    This endpoint returns the current status and progress of a workflow.
    """
    try:
        status = await orchestrator.get_workflow_status(session_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        return WorkflowStatus(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Emergency override endpoint
@app.post("/emergency/override/{session_id}")
async def emergency_override(
    session_id: str,
    override_data: Dict[str, Any],
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Emergency override for critical situations.
    
    This endpoint bypasses normal workflow for immediate action.
    """
    try:
        await orchestrator.emergency_override(session_id, override_data)
        
        return {
            "session_id": session_id,
            "status": "emergency_override_activated",
            "message": "Emergency override processed"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in emergency override: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Complete workflow endpoint
@app.post("/workflow/{session_id}/complete")
async def complete_workflow(
    session_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Complete a workflow session.
    
    This endpoint marks a workflow as completed and cleans up resources.
    """
    try:
        await orchestrator.complete_workflow(session_id)
        
        return {
            "session_id": session_id,
            "status": "completed",
            "message": "Workflow completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error completing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API documentation endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "MediSentinel",
        "description": "Agentic AI for Emergency-First Hospital Automation",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "agent_health": "/health/agents",
            "emergency_triage": "/emergency/triage",
            "schedule_appointment": "/appointments/schedule",
            "workflow_status": "/workflow/{session_id}",
            "emergency_override": "/emergency/override/{session_id}",
            "complete_workflow": "/workflow/{session_id}/complete"
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 