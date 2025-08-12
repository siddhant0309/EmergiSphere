"""
Smart Health Device Agent for MediSentinel

This agent handles all smart health device interactions including:
- Smartwatch medical report storage and retrieval
- Doctor device scanning and patient history access
- Emergency contact notifications
- Automatic emergency contact activation
- Device security and authentication
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .base_agent import BaseAgent


class SmartDeviceData(BaseModel):
    """Data structure for smart health device information."""
    device_id: str
    patient_id: str
    device_type: str = "smartwatch"  # smartwatch, fitness_tracker, etc.
    device_model: str
    firmware_version: str
    last_sync: datetime
    battery_level: int = Field(ge=0, le=100)
    is_connected: bool = True
    emergency_contacts: List[Dict[str, str]] = []
    medical_reports: List[Dict[str, Any]] = []
    vital_signs: Dict[str, Any] = {}
    emergency_thresholds: Dict[str, Any] = {}


class MedicalReport(BaseModel):
    """Structure for medical reports stored on smart devices."""
    report_id: str
    report_type: str  # lab_results, imaging, prescription, etc.
    report_date: datetime
    doctor_id: str
    hospital_id: str
    report_data: Dict[str, Any]
    is_encrypted: bool = True
    access_level: str = "restricted"  # public, restricted, emergency_only


class EmergencyContact(BaseModel):
    """Emergency contact information."""
    contact_id: str
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    notification_preferences: Dict[str, bool] = {
        "sms": True,
        "email": True,
        "push": True
    }
    is_primary: bool = False


class DeviceScanRequest(BaseModel):
    """Request for scanning a smart health device."""
    doctor_id: str
    device_id: str
    scan_type: str  # "medical_history", "emergency_contact", "vital_signs"
    access_code: Optional[str] = None
    emergency_override: bool = False


class SmartHealthDeviceAgent(BaseAgent):
    """
    Agent responsible for managing smart health device interactions.
    
    Handles:
    - Device registration and authentication
    - Medical report storage and encryption
    - Doctor device scanning
    - Emergency contact management
    - Automatic emergency detection and notification
    """
    
    def __init__(self):
        super().__init__()
        self.encryption_key = self._generate_encryption_key()
        self.registered_devices: Dict[str, SmartDeviceData] = {}
        self.device_sessions: Dict[str, Dict[str, Any]] = {}
        self.emergency_alerts: List[Dict[str, Any]] = []
        
        # Load existing devices (in production, this would come from database)
        self._load_sample_devices()
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for device data."""
        # In production, this would be stored securely and rotated regularly
        return Fernet.generate_key()
    
    def _load_sample_devices(self):
        """Load sample devices for demonstration purposes."""
        sample_device = SmartDeviceData(
            device_id="smartwatch_001",
            patient_id="patient_001",
            device_type="smartwatch",
            device_model="Apple Watch Series 9",
            firmware_version="10.1.1",
            last_sync=datetime.utcnow(),
            battery_level=85,
            emergency_contacts=[
                EmergencyContact(
                    contact_id="contact_001",
                    name="John Doe",
                    relationship="Spouse",
                    phone="+1-555-0123",
                    email="john.doe@email.com",
                    is_primary=True
                ).dict()
            ],
            medical_reports=[
                MedicalReport(
                    report_id="report_001",
                    report_type="lab_results",
                    report_date=datetime.utcnow() - timedelta(days=7),
                    doctor_id="doctor_001",
                    hospital_id="hospital_001",
                    report_data={
                        "blood_pressure": "120/80",
                        "heart_rate": "72",
                        "temperature": "98.6",
                        "glucose": "95"
                    }
                ).dict()
            ],
            vital_signs={
                "heart_rate": 72,
                "blood_pressure": "120/80",
                "temperature": 98.6,
                "oxygen_saturation": 98,
                "steps_today": 8500
            },
            emergency_thresholds={
                "heart_rate_min": 50,
                "heart_rate_max": 120,
                "blood_pressure_min": "90/60",
                "blood_pressure_max": "140/90",
                "temperature_min": 95.0,
                "temperature_max": 103.0
            }
        )
        
        self.registered_devices[sample_device.device_id] = sample_device
    
    async def process(self, context: Any) -> Dict[str, Any]:
        """
        Process smart health device requests.
        
        Args:
            context: Workflow context containing device interaction data
            
        Returns:
            Dictionary containing processing results
        """
        try:
            if isinstance(context, dict):
                action = context.get('action')
                
                if action == 'scan_device':
                    return await self.scan_device(DeviceScanRequest(**context.get('scan_data', {})))
                elif action == 'store_medical_report':
                    return await self.store_medical_report(context.get('report_data', {}))
                elif action == 'get_emergency_contacts':
                    return await self.get_emergency_contacts(context.get('device_id'))
                elif action == 'update_vital_signs':
                    return await self.update_vital_signs(context.get('device_id'), context.get('vital_signs', {}))
                elif action == 'check_emergency_conditions':
                    return await self.check_emergency_conditions(context.get('device_id'))
                else:
                    return {'error': 'Unknown action', 'action': action}
            
            return {'error': 'Invalid context format'}
            
        except Exception as e:
            self.logger.error(f"Error processing smart health device request: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def scan_device(self, scan_request: DeviceScanRequest) -> Dict[str, Any]:
        """
        Handle doctor scanning of smart health device.
        
        Args:
            scan_request: Device scan request details
            
        Returns:
            Device data and medical history
        """
        try:
            device_id = scan_request.device_id
            doctor_id = scan_request.doctor_id
            
            if device_id not in self.registered_devices:
                return {'error': 'Device not found', 'status': 'failed'}
            
            device = self.registered_devices[device_id]
            
            # Verify doctor access (in production, this would check permissions)
            if not self._verify_doctor_access(doctor_id, device.patient_id):
                return {'error': 'Access denied', 'status': 'failed'}
            
            # Create device session for tracking
            session_id = str(uuid4())
            self.device_sessions[session_id] = {
                'doctor_id': doctor_id,
                'device_id': device_id,
                'patient_id': device.patient_id,
                'scan_time': datetime.utcnow(),
                'scan_type': scan_request.scan_type
            }
            
            # Notify emergency contacts about device access
            await self._notify_emergency_contacts(
                device_id, 
                f"Device accessed by doctor {doctor_id}",
                "device_access"
            )
            
            # Return appropriate data based on scan type
            if scan_request.scan_type == "medical_history":
                return {
                    'status': 'success',
                    'session_id': session_id,
                    'patient_id': device.patient_id,
                    'medical_reports': device.medical_reports,
                    'vital_signs': device.vital_signs,
                    'scan_time': datetime.utcnow().isoformat()
                }
            elif scan_request.scan_type == "emergency_contact":
                return {
                    'status': 'success',
                    'session_id': session_id,
                    'emergency_contacts': device.emergency_contacts,
                    'scan_time': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'success',
                    'session_id': session_id,
                    'device_info': {
                        'device_type': device.device_type,
                        'device_model': device.device_model,
                        'firmware_version': device.firmware_version,
                        'battery_level': device.battery_level,
                        'last_sync': device.last_sync.isoformat()
                    },
                    'scan_time': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error scanning device: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def store_medical_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store medical report on smart device.
        
        Args:
            report_data: Medical report data to store
            
        Returns:
            Storage confirmation
        """
        try:
            device_id = report_data.get('device_id')
            if device_id not in self.registered_devices:
                return {'error': 'Device not found', 'status': 'failed'}
            
            device = self.registered_devices[device_id]
            
            # Create new medical report
            new_report = MedicalReport(
                report_id=str(uuid4()),
                report_type=report_data.get('report_type', 'general'),
                report_date=datetime.utcnow(),
                doctor_id=report_data.get('doctor_id'),
                hospital_id=report_data.get('hospital_id'),
                report_data=report_data.get('report_data', {}),
                is_encrypted=True
            )
            
            # Encrypt sensitive report data
            encrypted_data = self._encrypt_data(new_report.report_data)
            new_report.report_data = encrypted_data
            
            # Add to device
            device.medical_reports.append(new_report.dict())
            device.last_sync = datetime.utcnow()
            
            self.logger.info(f"Stored medical report {new_report.report_id} on device {device_id}")
            
            return {
                'status': 'success',
                'report_id': new_report.report_id,
                'stored_at': datetime.utcnow().isoformat(),
                'device_id': device_id
            }
            
        except Exception as e:
            self.logger.error(f"Error storing medical report: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def get_emergency_contacts(self, device_id: str) -> Dict[str, Any]:
        """
        Retrieve emergency contacts for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Emergency contact information
        """
        try:
            if device_id not in self.registered_devices:
                return {'error': 'Device not found', 'status': 'failed'}
            
            device = self.registered_devices[device_id]
            return {
                'status': 'success',
                'emergency_contacts': device.emergency_contacts,
                'device_id': device_id
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving emergency contacts: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def update_vital_signs(self, device_id: str, vital_signs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update vital signs from smart device.
        
        Args:
            device_id: Device identifier
            vital_signs: New vital signs data
            
        Returns:
            Update confirmation and emergency check results
        """
        try:
            if device_id not in self.registered_devices:
                return {'error': 'Device not found', 'status': 'failed'}
            
            device = self.registered_devices[device_id]
            
            # Update vital signs
            device.vital_signs.update(vital_signs)
            device.last_sync = datetime.utcnow()
            
            # Check for emergency conditions
            emergency_check = await self.check_emergency_conditions(device_id)
            
            return {
                'status': 'success',
                'vital_signs_updated': True,
                'last_sync': device.last_sync.isoformat(),
                'emergency_check': emergency_check,
                'device_id': device_id
            }
            
        except Exception as e:
            self.logger.error(f"Error updating vital signs: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def check_emergency_conditions(self, device_id: str) -> Dict[str, Any]:
        """
        Check if current vital signs indicate emergency conditions.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Emergency condition assessment
        """
        try:
            if device_id not in self.registered_devices:
                return {'error': 'Device not found', 'status': 'failed'}
            
            device = self.registered_devices[device_id]
            vital_signs = device.vital_signs
            thresholds = device.emergency_thresholds
            
            emergency_conditions = []
            is_emergency = False
            
            # Check heart rate
            if 'heart_rate' in vital_signs:
                hr = vital_signs['heart_rate']
                if hr < thresholds.get('heart_rate_min', 50) or hr > thresholds.get('heart_rate_max', 120):
                    emergency_conditions.append(f"Heart rate: {hr} (normal: {thresholds.get('heart_rate_min', 50)}-{thresholds.get('heart_rate_max', 120)})")
                    is_emergency = True
            
            # Check temperature
            if 'temperature' in vital_signs:
                temp = vital_signs['temperature']
                if temp < thresholds.get('temperature_min', 95.0) or temp > thresholds.get('temperature_max', 103.0):
                    emergency_conditions.append(f"Temperature: {temp}°F (normal: {thresholds.get('temperature_min', 95.0)}-{thresholds.get('temperature_max', 103.0)}°F)")
                    is_emergency = True
            
            # Check blood pressure (simplified)
            if 'blood_pressure' in vital_signs:
                bp = vital_signs['blood_pressure']
                # In production, this would parse systolic/diastolic properly
                if bp != "120/80":  # Simplified check
                    emergency_conditions.append(f"Blood pressure: {bp}")
                    is_emergency = True
            
            # If emergency detected, activate emergency protocols
            if is_emergency:
                await self._activate_emergency_protocols(device_id, emergency_conditions)
            
            return {
                'is_emergency': is_emergency,
                'emergency_conditions': emergency_conditions,
                'vital_signs': vital_signs,
                'thresholds': thresholds,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking emergency conditions: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def _activate_emergency_protocols(self, device_id: str, conditions: List[str]) -> None:
        """
        Activate emergency protocols when critical conditions are detected.
        
        Args:
            device_id: Device identifier
            conditions: List of emergency conditions detected
        """
        try:
            device = self.registered_devices[device_id]
            
            # Create emergency alert
            alert = {
                'alert_id': str(uuid4()),
                'device_id': device_id,
                'patient_id': device.patient_id,
                'alert_type': 'emergency_condition',
                'conditions': conditions,
                'timestamp': datetime.utcnow(),
                'status': 'active'
            }
            
            self.emergency_alerts.append(alert)
            
            # Notify all emergency contacts
            await self._notify_emergency_contacts(
                device_id,
                f"EMERGENCY: Patient {device.patient_id} has critical vital signs: {', '.join(conditions)}",
                "emergency_alert"
            )
            
            # Log emergency activation
            self.logger.warning(f"Emergency protocols activated for device {device_id}: {conditions}")
            
        except Exception as e:
            self.logger.error(f"Error activating emergency protocols: {e}")
    
    async def _notify_emergency_contacts(
        self, 
        device_id: str, 
        message: str, 
        notification_type: str
    ) -> None:
        """
        Notify emergency contacts about device events.
        
        Args:
            device_id: Device identifier
            message: Notification message
            notification_type: Type of notification
        """
        try:
            device = self.registered_devices[device_id]
            
            for contact in device.emergency_contacts:
                # In production, this would integrate with actual notification services
                notification = {
                    'contact_id': contact['contact_id'],
                    'contact_name': contact['name'],
                    'phone': contact['phone'],
                    'email': contact.get('email'),
                    'message': message,
                    'notification_type': notification_type,
                    'timestamp': datetime.utcnow(),
                    'device_id': device_id,
                    'patient_id': device.patient_id
                }
                
                # Send SMS (would integrate with Twilio or similar)
                if contact.get('notification_preferences', {}).get('sms', True):
                    await self._send_sms(contact['phone'], message)
                
                # Send email (would integrate with SendGrid or similar)
                if contact.get('email') and contact.get('notification_preferences', {}).get('email', True):
                    await self._send_email(contact['email'], f"Smart Health Device Alert - {notification_type}", message)
                
                self.logger.info(f"Notified emergency contact {contact['name']} about {notification_type}")
                
        except Exception as e:
            self.logger.error(f"Error notifying emergency contacts: {e}")
    
    async def _send_sms(self, phone: str, message: str) -> None:
        """Send SMS notification (placeholder for actual SMS service integration)."""
        # In production, this would integrate with Twilio or similar service
        self.logger.info(f"SMS sent to {phone}: {message[:50]}...")
    
    async def _send_email(self, email: str, subject: str, message: str) -> None:
        """Send email notification (placeholder for actual email service integration)."""
        # In production, this would integrate with SendGrid or similar service
        self.logger.info(f"Email sent to {email}: {subject}")
    
    def _verify_doctor_access(self, doctor_id: str, patient_id: str) -> bool:
        """
        Verify if doctor has access to patient's device data.
        
        Args:
            doctor_id: Doctor identifier
            patient_id: Patient identifier
            
        Returns:
            True if access is granted, False otherwise
        """
        # In production, this would check actual permissions from database
        # For now, return True for demonstration
        return True
    
    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive data before storing on device.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as base64 string
        """
        try:
            fernet = Fernet(self.encryption_key)
            json_data = json.dumps(data)
            encrypted = fernet.encrypt(json_data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            return json.dumps(data)  # Fallback to unencrypted
    
    def _decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt data retrieved from device.
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted data
        """
        try:
            fernet = Fernet(self.encryption_key)
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            return {}
    
    async def emergency_process(self, context: Any, override_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle emergency processing for smart health devices.
        
        Args:
            context: Workflow context
            override_data: Emergency override data
            
        Returns:
            Emergency processing results
        """
        try:
            device_id = override_data.get('device_id')
            if not device_id:
                return {'error': 'Device ID required for emergency processing', 'status': 'failed'}
            
            # Force emergency contact notification
            await self._notify_emergency_contacts(
                device_id,
                "EMERGENCY OVERRIDE: Device accessed in emergency mode",
                "emergency_override"
            )
            
            # Return device emergency data
            if device_id in self.registered_devices:
                device = self.registered_devices[device_id]
                return {
                    'emergency_processed': True,
                    'agent': self.agent_name,
                    'device_id': device_id,
                    'patient_id': device.patient_id,
                    'emergency_contacts': device.emergency_contacts,
                    'vital_signs': device.vital_signs,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'emergency_processed': True,
                    'agent': self.agent_name,
                    'error': 'Device not found',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error in emergency processing: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get current status of a smart health device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device status information
        """
        try:
            if device_id not in self.registered_devices:
                return {'error': 'Device not found', 'status': 'failed'}
            
            device = self.registered_devices[device_id]
            
            return {
                'status': 'success',
                'device_id': device_id,
                'patient_id': device.patient_id,
                'device_type': device.device_type,
                'device_model': device.device_model,
                'battery_level': device.battery_level,
                'is_connected': device.is_connected,
                'last_sync': device.last_sync.isoformat(),
                'firmware_version': device.firmware_version,
                'emergency_contacts_count': len(device.emergency_contacts),
                'medical_reports_count': len(device.medical_reports),
                'has_vital_signs': bool(device.vital_signs)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting device status: {e}")
            return {'error': str(e), 'status': 'failed'}
