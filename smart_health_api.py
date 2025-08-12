"""
Smart Health Device API for MediSentinel

This module provides REST API endpoints for smart health device operations:
- Device registration and management
- Doctor device scanning
- Medical report storage and retrieval
- Emergency contact management
- Vital signs monitoring
- Emergency condition detection
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from agents.smart_health_device_agent import (
    SmartHealthDeviceAgent,
    SmartDeviceData,
    MedicalReport,
    EmergencyContact,
    DeviceScanRequest
)

# Initialize FastAPI app
app = FastAPI(
    title="EmergiSphere Smart Health Device API",
    description="API for managing smart health devices, medical reports, and emergency contacts",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Initialize agent
smart_device_agent = SmartHealthDeviceAgent()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Request/Response Models
class DeviceRegistrationRequest(BaseModel):
    """Request model for registering a new smart health device."""
    patient_id: str
    device_type: str = "smartwatch"
    device_model: str
    firmware_version: str
    emergency_contacts: List[Dict[str, Any]] = []
    emergency_thresholds: Dict[str, Any] = {}


class DeviceScanResponse(BaseModel):
    """Response model for device scanning operations."""
    status: str
    session_id: Optional[str] = None
    patient_id: Optional[str] = None
    medical_reports: Optional[List[Dict[str, Any]]] = None
    vital_signs: Optional[Dict[str, Any]] = None
    emergency_contacts: Optional[List[Dict[str, Any]]] = None
    device_info: Optional[Dict[str, Any]] = None
    scan_time: Optional[str] = None
    error: Optional[str] = None


class MedicalReportRequest(BaseModel):
    """Request model for storing medical reports on devices."""
    device_id: str
    report_type: str
    doctor_id: str
    hospital_id: str
    report_data: Dict[str, Any]
    access_level: str = "restricted"


class VitalSignsUpdateRequest(BaseModel):
    """Request model for updating vital signs from devices."""
    device_id: str
    vital_signs: Dict[str, Any]


class EmergencyContactRequest(BaseModel):
    """Request model for managing emergency contacts."""
    device_id: str
    contact: Dict[str, Any]


# Utility Functions
async def verify_doctor_access(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify doctor access token and return doctor ID."""
    # In production, this would validate JWT tokens and check permissions
    # For demonstration, we'll use a simple token format: "doctor_<id>"
    token = credentials.credentials
    
    if not token.startswith("doctor_"):
        raise HTTPException(status_code=401, detail="Invalid doctor token")
    
    doctor_id = token.replace("doctor_", "")
    return doctor_id


# API Endpoints

@app.post("/devices/register", response_model=Dict[str, Any])
async def register_device(request: DeviceRegistrationRequest):
    """
    Register a new smart health device.
    
    This endpoint allows patients to register their smart health devices
    with the MediSentinel system for medical report storage and monitoring.
    """
    try:
        # Generate device ID
        device_id = f"{request.device_type}_{request.patient_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create device data
        device_data = SmartDeviceData(
            device_id=device_id,
            patient_id=request.patient_id,
            device_type=request.device_type,
            device_model=request.device_model,
            firmware_version=request.firmware_version,
            last_sync=datetime.utcnow(),
            battery_level=100,
            emergency_contacts=request.emergency_contacts,
            emergency_thresholds=request.emergency_thresholds
        )
        
        # Register device with agent
        smart_device_agent.registered_devices[device_id] = device_data
        
        logger.info(f"Registered new device {device_id} for patient {request.patient_id}")
        
        return {
            "status": "success",
            "device_id": device_id,
            "message": "Device registered successfully",
            "registered_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register device: {str(e)}")


@app.post("/devices/scan", response_model=DeviceScanResponse)
async def scan_device(
    request: DeviceScanRequest,
    doctor_id: str = Depends(verify_doctor_access)
):
    """
    Scan a smart health device to access patient information.
    
    Doctors can scan patient devices to access:
    - Medical history and reports
    - Emergency contact information
    - Current vital signs
    - Device status information
    """
    try:
        # Update request with verified doctor ID
        request.doctor_id = doctor_id
        
        # Process scan request through agent
        result = await smart_device_agent.scan_device(request)
        
        if result.get('status') == 'success':
            return DeviceScanResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Scan failed'))
            
    except Exception as e:
        logger.error(f"Error scanning device: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan device: {str(e)}")


@app.post("/devices/{device_id}/reports", response_model=Dict[str, Any])
async def store_medical_report(
    device_id: str,
    request: MedicalReportRequest,
    doctor_id: str = Depends(verify_doctor_access)
):
    """
    Store a medical report on a smart health device.
    
    Doctors can store medical reports, lab results, prescriptions,
    and other medical documents directly on patient devices.
    """
    try:
        # Prepare report data
        report_data = {
            'device_id': device_id,
            'report_type': request.report_type,
            'doctor_id': doctor_id,
            'hospital_id': request.hospital_id,
            'report_data': request.report_data
        }
        
        # Store report through agent
        result = await smart_device_agent.store_medical_report(report_data)
        
        if result.get('status') == 'success':
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to store report'))
            
    except Exception as e:
        logger.error(f"Error storing medical report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store medical report: {str(e)}")


@app.get("/devices/{device_id}/reports", response_model=Dict[str, Any])
async def get_medical_reports(
    device_id: str,
    doctor_id: str = Depends(verify_doctor_access)
):
    """
    Retrieve medical reports stored on a device.
    
    Doctors can access all medical reports stored on a patient's
    smart health device for comprehensive care coordination.
    """
    try:
        # Create scan request for medical history
        scan_request = DeviceScanRequest(
            doctor_id=doctor_id,
            device_id=device_id,
            scan_type="medical_history"
        )
        
        # Get reports through agent
        result = await smart_device_agent.scan_device(scan_request)
        
        if result.get('status') == 'success':
            return {
                "status": "success",
                "device_id": device_id,
                "medical_reports": result.get('medical_reports', []),
                "vital_signs": result.get('vital_signs', {}),
                "retrieved_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to retrieve reports'))
            
    except Exception as e:
        logger.error(f"Error retrieving medical reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve medical reports: {str(e)}")


@app.post("/devices/{device_id}/vital-signs", response_model=Dict[str, Any])
async def update_vital_signs(
    device_id: str,
    request: VitalSignsUpdateRequest
):
    """
    Update vital signs from a smart health device.
    
    Smart devices can continuously update vital signs and trigger
    emergency alerts when critical thresholds are exceeded.
    """
    try:
        # Update vital signs through agent
        result = await smart_device_agent.update_vital_signs(device_id, request.vital_signs)
        
        if result.get('status') == 'success':
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to update vital signs'))
            
    except Exception as e:
        logger.error(f"Error updating vital signs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update vital signs: {str(e)}")


@app.get("/devices/{device_id}/vital-signs", response_model=Dict[str, Any])
async def get_vital_signs(
    device_id: str,
    doctor_id: str = Depends(verify_doctor_access)
):
    """
    Get current vital signs from a smart health device.
    
    Doctors can access real-time vital signs data for
    immediate patient assessment and monitoring.
    """
    try:
        # Create scan request for vital signs
        scan_request = DeviceScanRequest(
            doctor_id=doctor_id,
            device_id=device_id,
            scan_type="vital_signs"
        )
        
        # Get vital signs through agent
        result = await smart_device_agent.scan_device(scan_request)
        
        if result.get('status') == 'success':
            return {
                "status": "success",
                "device_id": device_id,
                "vital_signs": result.get('vital_signs', {}),
                "retrieved_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to retrieve vital signs'))
            
    except Exception as e:
        logger.error(f"Error retrieving vital signs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vital signs: {str(e)}")


@app.get("/devices/{device_id}/emergency-contacts", response_model=Dict[str, Any])
async def get_emergency_contacts(
    device_id: str,
    doctor_id: str = Depends(verify_doctor_access)
):
    """
    Get emergency contacts for a smart health device.
    
    Doctors can access emergency contact information for
    immediate family notification in critical situations.
    """
    try:
        # Get emergency contacts through agent
        result = await smart_device_agent.get_emergency_contacts(device_id)
        
        if result.get('status') == 'success':
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to retrieve emergency contacts'))
            
    except Exception as e:
        logger.error(f"Error retrieving emergency contacts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emergency contacts: {str(e)}")


@app.post("/devices/{device_id}/emergency-contacts", response_model=Dict[str, Any])
async def add_emergency_contact(
    device_id: str,
    request: EmergencyContactRequest
):
    """
    Add an emergency contact to a smart health device.
    
    Patients can add family members, friends, or healthcare
    providers as emergency contacts for immediate notification.
    """
    try:
        # Validate device exists
        if device_id not in smart_device_agent.registered_devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device = smart_device_agent.registered_devices[device_id]
        
        # Add new contact
        new_contact = EmergencyContact(**request.contact)
        device.emergency_contacts.append(new_contact.dict())
        
        logger.info(f"Added emergency contact {new_contact.name} to device {device_id}")
        
        return {
            "status": "success",
            "message": "Emergency contact added successfully",
            "contact_id": new_contact.contact_id,
            "added_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error adding emergency contact: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add emergency contact: {str(e)}")


@app.post("/devices/{device_id}/emergency-check", response_model=Dict[str, Any])
async def check_emergency_conditions(device_id: str):
    """
    Manually check for emergency conditions on a device.
    
    This endpoint can be used to manually trigger emergency
    condition assessment and contact notification.
    """
    try:
        # Check emergency conditions through agent
        result = await smart_device_agent.check_emergency_conditions(device_id)
        
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to check emergency conditions'))
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking emergency conditions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check emergency conditions: {str(e)}")


@app.get("/devices/{device_id}/status", response_model=Dict[str, Any])
async def get_device_status(device_id: str):
    """
    Get current status of a smart health device.
    
    Provides comprehensive device information including
    battery level, connection status, and data counts.
    """
    try:
        # Get device status through agent
        result = await smart_device_agent.get_device_status(device_id)
        
        if result.get('status') == 'success':
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to get device status'))
            
    except Exception as e:
        logger.error(f"Error getting device status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get device status: {str(e)}")


@app.post("/devices/{device_id}/emergency-override", response_model=Dict[str, Any])
async def emergency_override(
    device_id: str,
    doctor_id: str = Depends(verify_doctor_access)
):
    """
    Emergency override for device access.
    
    Allows doctors to bypass normal security protocols
    in emergency situations for immediate patient care.
    """
    try:
        # Process emergency override through agent
        result = await smart_device_agent.emergency_process(
            context={"device_id": device_id},
            override_data={"device_id": device_id}
        )
        
        if result.get('emergency_processed'):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Emergency override failed'))
            
    except Exception as e:
        logger.error(f"Error in emergency override: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency override failed: {str(e)}")


@app.get("/devices", response_model=Dict[str, Any])
async def list_devices():
    """
    List all registered smart health devices.
    
    Provides an overview of all devices in the system
    for administrative and monitoring purposes.
    """
    try:
        devices = []
        for device_id, device in smart_device_agent.registered_devices.items():
            devices.append({
                "device_id": device_id,
                "patient_id": device.patient_id,
                "device_type": device.device_type,
                "device_model": device.device_model,
                "battery_level": device.battery_level,
                "is_connected": device.is_connected,
                "last_sync": device.last_sync.isoformat(),
                "emergency_contacts_count": len(device.emergency_contacts),
                "medical_reports_count": len(device.medical_reports)
            })
        
        return {
            "status": "success",
            "devices": devices,
            "total_count": len(devices),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list devices: {str(e)}")


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for the Smart Health Device API."""
    try:
        # Check agent health
        agent_healthy = await smart_device_agent.health_check()
        
        return {
            "status": "healthy" if agent_healthy else "unhealthy",
            "service": "Smart Health Device API",
            "agent_healthy": agent_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "registered_devices": len(smart_device_agent.registered_devices),
            "active_sessions": len(smart_device_agent.device_sessions),
            "emergency_alerts": len(smart_device_agent.emergency_alerts)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "Smart Health Device API",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
