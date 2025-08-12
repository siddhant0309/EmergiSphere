"""
Smart Health Device Demo Script

This script demonstrates the smart health device functionality:
- Device registration
- Doctor device scanning
- Medical report storage
- Emergency contact management
- Vital signs monitoring
- Emergency condition detection
"""

import asyncio
import json
from datetime import datetime, timedelta
from agents.smart_health_device_agent import SmartHealthDeviceAgent


async def demo_smart_health_devices():
    """Demonstrate smart health device functionality."""
    
    print("🏥 EmergiSphere Smart Health Device Demo")
    print("=" * 50)
    
    # Initialize the smart health device agent
    agent = SmartHealthDeviceAgent()
    
    # Demo 1: Device Registration
    print("\n📱 Demo 1: Device Registration")
    print("-" * 30)
    
    # Register a new device
    new_device_data = {
        "patient_id": "patient_002",
        "device_type": "smartwatch",
        "device_model": "Samsung Galaxy Watch 6",
        "firmware_version": "1.2.3",
        "emergency_contacts": [
            {
                "contact_id": "contact_002",
                "name": "Jane Smith",
                "relationship": "Daughter",
                "phone": "+1-555-0456",
                "email": "jane.smith@email.com",
                "is_primary": True
            }
        ],
        "emergency_thresholds": {
            "heart_rate_min": 45,
            "heart_rate_max": 130,
            "blood_pressure_min": "85/55",
            "blood_pressure_max": "150/95",
            "temperature_min": 94.0,
            "temperature_max": 104.0
        }
    }
    
    # Create device data
    from agents.smart_health_device_agent import SmartDeviceData, EmergencyContact
    device_data = SmartDeviceData(
        device_id="smartwatch_002",
        patient_id=new_device_data["patient_id"],
        device_type=new_device_data["device_type"],
        device_model=new_device_data["device_model"],
        firmware_version=new_device_data["firmware_version"],
        last_sync=datetime.utcnow(),
        battery_level=95,
        emergency_contacts=[EmergencyContact(**contact).dict() for contact in new_device_data["emergency_contacts"]],
        emergency_thresholds=new_device_data["emergency_thresholds"]
    )
    
    agent.registered_devices[device_data.device_id] = device_data
    
    print(f"✅ Registered device: {device_data.device_id}")
    print(f"   Patient: {device_data.patient_id}")
    print(f"   Model: {device_data.device_model}")
    print(f"   Emergency contacts: {len(device_data.emergency_contacts)}")
    
    # Demo 2: Doctor Device Scanning
    print("\n🔍 Demo 2: Doctor Device Scanning")
    print("-" * 30)
    
    # Simulate doctor scanning device for medical history
    scan_request = {
        "doctor_id": "doctor_002",
        "device_id": "smartwatch_002",
        "scan_type": "medical_history"
    }
    
    scan_result = await agent.scan_device(scan_request)
    
    if scan_result.get('status') == 'success':
        print(f"✅ Device scan successful")
        print(f"   Session ID: {scan_result.get('session_id')}")
        print(f"   Patient ID: {scan_result.get('patient_id')}")
        print(f"   Medical reports: {len(scan_result.get('medical_reports', []))}")
        print(f"   Vital signs available: {bool(scan_result.get('vital_signs'))}")
    else:
        print(f"❌ Device scan failed: {scan_result.get('error')}")
    
    # Demo 3: Medical Report Storage
    print("\n📋 Demo 3: Medical Report Storage")
    print("-" * 30)
    
    # Store a new medical report
    report_data = {
        "device_id": "smartwatch_002",
        "report_type": "prescription",
        "doctor_id": "doctor_002",
        "hospital_id": "hospital_001",
        "report_data": {
            "medication": "Lisinopril 10mg",
            "dosage": "1 tablet daily",
            "duration": "30 days",
            "instructions": "Take in the morning with food",
            "side_effects": ["Dizziness", "Dry cough", "Fatigue"]
        }
    }
    
    store_result = await agent.store_medical_report(report_data)
    
    if store_result.get('status') == 'success':
        print(f"✅ Medical report stored successfully")
        print(f"   Report ID: {store_result.get('report_id')}")
        print(f"   Stored at: {store_result.get('stored_at')}")
    else:
        print(f"❌ Failed to store report: {store_result.get('error')}")
    
    # Demo 4: Vital Signs Update and Emergency Detection
    print("\n💓 Demo 4: Vital Signs Update & Emergency Detection")
    print("-" * 30)
    
    # Update vital signs with normal values
    normal_vitals = {
        "heart_rate": 75,
        "blood_pressure": "118/78",
        "temperature": 98.2,
        "oxygen_saturation": 99,
        "steps_today": 12000
    }
    
    update_result = await agent.update_vital_signs("smartwatch_002", normal_vitals)
    
    if update_result.get('status') == 'success':
        print(f"✅ Vital signs updated (normal)")
        print(f"   Heart rate: {normal_vitals['heart_rate']} bpm")
        print(f"   Blood pressure: {normal_vitals['blood_pressure']}")
        print(f"   Temperature: {normal_vitals['temperature']}°F")
        
        # Check emergency conditions
        emergency_check = update_result.get('emergency_check', {})
        if emergency_check.get('is_emergency'):
            print(f"🚨 EMERGENCY DETECTED: {emergency_check.get('emergency_conditions')}")
        else:
            print(f"✅ No emergency conditions detected")
    else:
        print(f"❌ Failed to update vital signs: {update_result.get('error')}")
    
    # Demo 5: Emergency Scenario
    print("\n🚨 Demo 5: Emergency Scenario")
    print("-" * 30)
    
    # Update vital signs with emergency values
    emergency_vitals = {
        "heart_rate": 45,  # Below normal threshold
        "blood_pressure": "85/55",  # Below normal threshold
        "temperature": 94.5,  # Below normal threshold
        "oxygen_saturation": 92,
        "steps_today": 500
    }
    
    emergency_update = await agent.update_vital_signs("smartwatch_002", emergency_vitals)
    
    if emergency_update.get('status') == 'success':
        print(f"✅ Vital signs updated (emergency values)")
        print(f"   Heart rate: {emergency_vitals['heart_rate']} bpm (CRITICAL)")
        print(f"   Blood pressure: {emergency_vitals['blood_pressure']} (CRITICAL)")
        print(f"   Temperature: {emergency_vitals['temperature']}°F (CRITICAL)")
        
        # Check emergency conditions
        emergency_check = emergency_update.get('emergency_check', {})
        if emergency_check.get('is_emergency'):
            print(f"🚨 EMERGENCY DETECTED!")
            print(f"   Conditions: {emergency_check.get('emergency_conditions')}")
            print(f"   Emergency protocols activated")
            print(f"   Emergency contacts notified")
        else:
            print(f"✅ No emergency conditions detected")
    else:
        print(f"❌ Failed to update emergency vital signs: {emergency_update.get('error')}")
    
    # Demo 6: Device Status and Information
    print("\n📊 Demo 6: Device Status & Information")
    print("-" * 30)
    
    # Get device status
    device_status = await agent.get_device_status("smartwatch_002")
    
    if device_status.get('status') == 'success':
        print(f"✅ Device status retrieved")
        print(f"   Device ID: {device_status.get('device_id')}")
        print(f"   Patient ID: {device_status.get('patient_id')}")
        print(f"   Device Type: {device_status.get('device_type')}")
        print(f"   Model: {device_status.get('device_model')}")
        print(f"   Battery: {device_status.get('battery_level')}%")
        print(f"   Connected: {device_status.get('is_connected')}")
        print(f"   Last Sync: {device_status.get('last_sync')}")
        print(f"   Emergency Contacts: {device_status.get('emergency_contacts_count')}")
        print(f"   Medical Reports: {device_status.get('medical_reports_count')}")
        print(f"   Has Vital Signs: {device_status.get('has_vital_signs')}")
    else:
        print(f"❌ Failed to get device status: {device_status.get('error')}")
    
    # Demo 7: Emergency Contact Management
    print("\n👥 Demo 7: Emergency Contact Management")
    print("-" * 30)
    
    # Get emergency contacts
    contacts_result = await agent.get_emergency_contacts("smartwatch_002")
    
    if contacts_result.get('status') == 'success':
        contacts = contacts_result.get('emergency_contacts', [])
        print(f"✅ Emergency contacts retrieved: {len(contacts)} contacts")
        
        for contact in contacts:
            print(f"   📞 {contact['name']} ({contact['relationship']})")
            print(f"      Phone: {contact['phone']}")
            if contact.get('email'):
                print(f"      Email: {contact['email']}")
            print(f"      Primary: {contact['is_primary']}")
            print()
    else:
        print(f"❌ Failed to get emergency contacts: {contacts_result.get('error')}")
    
    # Demo 8: Emergency Override
    print("\n🚨 Demo 8: Emergency Override")
    print("-" * 30)
    
    # Simulate emergency override
    emergency_override = await agent.emergency_process(
        context={"device_id": "smartwatch_002"},
        override_data={"device_id": "smartwatch_002"}
    )
    
    if emergency_override.get('emergency_processed'):
        print(f"✅ Emergency override processed")
        print(f"   Device ID: {emergency_override.get('device_id')}")
        print(f"   Patient ID: {emergency_override.get('patient_id')}")
        print(f"   Emergency contacts: {len(emergency_override.get('emergency_contacts', []))}")
        print(f"   Vital signs available: {bool(emergency_override.get('vital_signs'))}")
    else:
        print(f"❌ Emergency override failed: {emergency_override.get('error')}")
    
    # Demo 9: System Overview
    print("\n🏥 Demo 9: System Overview")
    print("-" * 30)
    
    print(f"📱 Registered Devices: {len(agent.registered_devices)}")
    print(f"🔐 Active Sessions: {len(agent.device_sessions)}")
    print(f"🚨 Emergency Alerts: {len(agent.emergency_alerts)}")
    
    # Show all devices
    print(f"\n📋 Device List:")
    for device_id, device in agent.registered_devices.items():
        print(f"   • {device_id}: {device.device_model} ({device.patient_id})")
        print(f"     Battery: {device.battery_level}% | Reports: {len(device.medical_reports)}")
    
    # Show emergency alerts
    if agent.emergency_alerts:
        print(f"\n🚨 Emergency Alerts:")
        for alert in agent.emergency_alerts:
            print(f"   • {alert['alert_type']}: {alert['conditions']}")
            print(f"     Device: {alert['device_id']} | Patient: {alert['patient_id']}")
            print(f"     Time: {alert['timestamp']}")
    
    print("\n" + "=" * 50)
    print("🎉 Smart Health Device Demo Completed!")
    print("=" * 50)


async def demo_api_endpoints():
    """Demonstrate API endpoint functionality."""
    
    print("\n🌐 Smart Health Device API Demo")
    print("=" * 50)
    
    # Import the API
    from smart_health_api import app
    from fastapi.testclient import TestClient
    
    # Create test client
    client = TestClient(app)
    
    # Test health endpoint
    print("\n🔍 Testing Health Endpoint")
    print("-" * 30)
    
    response = client.get("/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ Health check successful")
        print(f"   Status: {health_data.get('status')}")
        print(f"   Service: {health_data.get('service')}")
        print(f"   Agent Healthy: {health_data.get('agent_healthy')}")
        print(f"   Registered Devices: {health_data.get('registered_devices')}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    # Test device listing
    print("\n📱 Testing Device Listing")
    print("-" * 30)
    
    response = client.get("/devices")
    if response.status_code == 200:
        devices_data = response.json()
        print(f"✅ Device listing successful")
        print(f"   Total Devices: {devices_data.get('total_count')}")
        for device in devices_data.get('devices', []):
            print(f"   • {device['device_id']}: {device['device_model']}")
    else:
        print(f"❌ Device listing failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🌐 API Demo Completed!")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 Starting EmergiSphere Smart Health Device Demo")
    
    # Run the main demo
    asyncio.run(demo_smart_health_devices())
    
    # Run the API demo
    asyncio.run(demo_api_endpoints())
    
    print("\n✨ Demo completed successfully!")
    print("\n📚 Next Steps:")
    print("   1. Run the Smart Health Device API: python smart_health_api.py")
    print("   2. Access the API documentation: http://localhost:8001/docs")
    print("   3. Test the endpoints with the provided examples")
    print("   4. Integrate with your existing EmergiSphere system")
