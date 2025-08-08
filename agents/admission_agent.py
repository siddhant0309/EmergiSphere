"""
MediSentinel Admission Agent

This agent handles patient registration, ID verification, and admission processes.
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import uuid4
import json

from pydantic import BaseModel, ValidationError
from openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
# import pytesseract  # Uncomment when pytesseract is installed
from PIL import Image
import io
import base64

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PatientInfo(BaseModel):
    """Patient information model."""
    name: str
    date_of_birth: str
    gender: str
    contact_number: str
    emergency_contact: str
    address: str
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None


class AdmissionInput(BaseModel):
    """Input data for admission process."""
    patient_info: Optional[PatientInfo] = None
    emergency_level: Optional[str] = None
    medical_condition: Optional[str] = None
    required_resources: Optional[List[str]] = None
    legal_case: Optional[bool] = False
    police_case_number: Optional[str] = None
    accident_details: Optional[Dict[str, Any]] = None
    documents: Optional[List[str]] = None  # Base64 encoded documents
    voice_input: Optional[str] = None
    text_input: Optional[str] = None


class AdmissionResult(BaseModel):
    """Result of admission process."""
    patient_id: str
    admission_status: str  # "admitted", "pending", "rejected"
    bed_assigned: Optional[str] = None
    ward_assigned: Optional[str] = None
    admission_type: str  # "emergency", "regular", "legal"
    verification_status: Dict[str, bool]
    insurance_verified: bool
    legal_case_registered: bool
    estimated_stay_duration: Optional[str] = None
    admission_notes: str
    next_steps: List[str]
    confidence_score: float


class AdmissionAgent(BaseAgent):
    """
    Agent for handling patient admission and registration.
    
    Handles:
    - Patient registration and ID verification
    - Emergency vs regular admission flows
    - Document processing and OCR
    - Insurance verification
    - Bed allocation
    - Legal case integration
    """
    
    def __init__(self):
        super().__init__()
        self.llm = OpenAI(temperature=0.1)
        self.admission_prompt = self._create_admission_prompt()
        self.chain = self.admission_prompt | self.llm | StrOutputParser()
        
        # Hospital capacity and bed management
        self.ward_capacity = {
            'emergency': {'beds': 20, 'available': 15},
            'icu': {'beds': 10, 'available': 3},
            'general': {'beds': 50, 'available': 25},
            'pediatric': {'beds': 15, 'available': 8},
            'maternity': {'beds': 12, 'available': 6}
        }
        
        # Insurance providers database (mock)
        self.insurance_providers = {
            'blue_cross': {'name': 'Blue Cross Blue Shield', 'verification_url': 'api.bluecross.com'},
            'aetna': {'name': 'Aetna', 'verification_url': 'api.aetna.com'},
            'cigna': {'name': 'Cigna', 'verification_url': 'api.cigna.com'},
            'united_health': {'name': 'UnitedHealth Group', 'verification_url': 'api.unitedhealth.com'}
        }
    
    async def process(self, context: Any) -> Dict[str, Any]:
        """
        Process patient admission.
        
        Args:
            context: Workflow context containing patient data and triage results
            
        Returns:
            Admission results including patient ID, bed assignment, etc.
        """
        try:
            # Extract admission input from context
            admission_input = self._extract_admission_input(context)
            
            # Process admission based on workflow type
            if context.workflow_type == "emergency":
                admission_result = await self._process_emergency_admission(admission_input, context)
            else:
                admission_result = await self._process_regular_admission(admission_input, context)
            
            # Log the admission
            await self._log_admission(context.session_id, admission_input, admission_result)
            
            # Update context with admission results
            return {
                'patient_id': admission_result.patient_id,
                'admission_status': admission_result.admission_status,
                'bed_assigned': admission_result.bed_assigned,
                'ward_assigned': admission_result.ward_assigned,
                'admission_type': admission_result.admission_type,
                'verification_status': admission_result.verification_status,
                'insurance_verified': admission_result.insurance_verified,
                'legal_case_registered': admission_result.legal_case_registered,
                'estimated_stay_duration': admission_result.estimated_stay_duration,
                'admission_notes': admission_result.admission_notes,
                'next_steps': admission_result.next_steps,
                'admission_confidence': admission_result.confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error in admission process: {e}")
            # Return default admission result in case of error
            return {
                'patient_id': f"EMERGENCY_{uuid4().hex[:8].upper()}",
                'admission_status': 'admitted',
                'bed_assigned': 'ER-01',
                'ward_assigned': 'emergency',
                'admission_type': 'emergency',
                'verification_status': {'id_verified': False, 'insurance_verified': False},
                'insurance_verified': False,
                'legal_case_registered': False,
                'estimated_stay_duration': '24-48 hours',
                'admission_notes': f'Emergency admission due to error: {str(e)}',
                'next_steps': ['immediate_medical_attention', 'complete_registration_later'],
                'admission_confidence': 0.0
            }
    
    def _extract_admission_input(self, context: Any) -> AdmissionInput:
        """Extract admission input data from workflow context."""
        metadata = context.metadata
        
        # Extract patient info if available
        patient_info = None
        if metadata.get('patient_info'):
            try:
                patient_info = PatientInfo(**metadata['patient_info'])
            except ValidationError as e:
                logger.warning(f"Invalid patient info: {e}")
        
        return AdmissionInput(
            patient_info=patient_info,
            emergency_level=metadata.get('emergency_level'),
            medical_condition=metadata.get('medical_condition'),
            required_resources=metadata.get('required_resources'),
            legal_case=metadata.get('legal_case', False),
            police_case_number=metadata.get('police_case_number'),
            accident_details=metadata.get('accident_details'),
            documents=metadata.get('documents'),
            voice_input=metadata.get('voice_input'),
            text_input=metadata.get('text_input')
        )
    
    async def _process_emergency_admission(self, admission_input: AdmissionInput, context: Any) -> AdmissionResult:
        """Process emergency admission with minimal paperwork."""
        logger.info(f"Processing emergency admission for session {context.session_id}")
        
        # Generate emergency patient ID
        patient_id = f"EMERGENCY_{uuid4().hex[:8].upper()}"
        
        # Extract patient info from voice/text input if not provided
        if not admission_input.patient_info:
            patient_info = await self._extract_patient_info_from_input(
                admission_input.voice_input or admission_input.text_input
            )
        else:
            patient_info = admission_input.patient_info
        
        # Determine appropriate ward and bed
        ward_assigned, bed_assigned = await self._allocate_emergency_bed(
            admission_input.emergency_level,
            admission_input.required_resources
        )
        
        # Process legal case if applicable
        legal_case_registered = False
        if admission_input.legal_case:
            legal_case_registered = await self._register_legal_case(
                patient_id, admission_input.police_case_number, admission_input.accident_details
            )
        
        # Quick insurance verification (can be completed later)
        insurance_verified = await self._quick_insurance_check(patient_info)
        
        # Generate admission notes
        admission_notes = await self._generate_admission_notes(
            patient_info, admission_input, ward_assigned, legal_case_registered
        )
        
        return AdmissionResult(
            patient_id=patient_id,
            admission_status='admitted',
            bed_assigned=bed_assigned,
            ward_assigned=ward_assigned,
            admission_type='emergency',
            verification_status={
                'id_verified': patient_info is not None,
                'insurance_verified': insurance_verified,
                'legal_case_registered': legal_case_registered
            },
            insurance_verified=insurance_verified,
            legal_case_registered=legal_case_registered,
            estimated_stay_duration=self._estimate_stay_duration(admission_input.medical_condition),
            admission_notes=admission_notes,
            next_steps=['immediate_medical_attention', 'complete_registration_later'],
            confidence_score=0.85
        )
    
    async def _process_regular_admission(self, admission_input: AdmissionInput, context: Any) -> AdmissionResult:
        """Process regular appointment admission with full verification."""
        logger.info(f"Processing regular admission for session {context.session_id}")
        
        # Validate patient info
        if not admission_input.patient_info:
            raise ValueError("Patient information is required for regular admission")
        
        patient_info = admission_input.patient_info
        
        # Generate patient ID
        patient_id = await self._generate_patient_id(patient_info)
        
        # Verify patient identity
        id_verified = await self._verify_patient_identity(patient_info)
        
        # Process documents if provided
        documents_processed = False
        if admission_input.documents:
            documents_processed = await self._process_documents(admission_input.documents)
        
        # Verify insurance
        insurance_verified = await self._verify_insurance(patient_info)
        
        # Allocate bed for regular admission
        ward_assigned, bed_assigned = await self._allocate_regular_bed(
            admission_input.medical_condition
        )
        
        # Generate admission notes
        admission_notes = await self._generate_admission_notes(
            patient_info, admission_input, ward_assigned, False
        )
        
        return AdmissionResult(
            patient_id=patient_id,
            admission_status='admitted' if id_verified else 'pending',
            bed_assigned=bed_assigned,
            ward_assigned=ward_assigned,
            admission_type='regular',
            verification_status={
                'id_verified': id_verified,
                'insurance_verified': insurance_verified,
                'documents_processed': documents_processed
            },
            insurance_verified=insurance_verified,
            legal_case_registered=False,
            estimated_stay_duration=self._estimate_stay_duration(admission_input.medical_condition),
            admission_notes=admission_notes,
            next_steps=['complete_registration', 'medical_evaluation'],
            confidence_score=0.95 if id_verified else 0.70
        )
    
    async def _extract_patient_info_from_input(self, input_text: str) -> Optional[PatientInfo]:
        """Extract patient information from voice or text input using AI."""
        if not input_text:
            return None
        
        try:
            # Use LLM to extract structured patient info
            prompt = f"""
            Extract patient information from the following text. Return as JSON:
            
            Text: {input_text}
            
            Expected JSON format:
            {{
                "name": "Full Name",
                "date_of_birth": "YYYY-MM-DD",
                "gender": "M/F/Other",
                "contact_number": "Phone Number",
                "emergency_contact": "Emergency Contact",
                "address": "Address",
                "insurance_provider": "Insurance Provider",
                "insurance_number": "Insurance Number"
            }}
            
            If information is not available, use null for that field.
            """
            
            response = await self.chain.ainvoke({"context": prompt, "instructions": "Extract patient information"})
            
            # Parse JSON response
            try:
                patient_data = json.loads(response)
                return PatientInfo(**patient_data)
            except (json.JSONDecodeError, ValidationError):
                logger.warning("Failed to parse patient info from LLM response")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting patient info: {e}")
            return None
    
    async def _allocate_emergency_bed(self, emergency_level: str, required_resources: List[str]) -> tuple[str, str]:
        """Allocate appropriate bed for emergency admission."""
        if emergency_level == 'critical' or 'icu' in required_resources:
            if self.ward_capacity['icu']['available'] > 0:
                self.ward_capacity['icu']['available'] -= 1
                return 'icu', f"ICU-{self.ward_capacity['icu']['beds'] - self.ward_capacity['icu']['available']:02d}"
        
        if self.ward_capacity['emergency']['available'] > 0:
            self.ward_capacity['emergency']['available'] -= 1
            return 'emergency', f"ER-{self.ward_capacity['emergency']['beds'] - self.ward_capacity['emergency']['available']:02d}"
        
        # Fallback to general ward
        if self.ward_capacity['general']['available'] > 0:
            self.ward_capacity['general']['available'] -= 1
            return 'general', f"GEN-{self.ward_capacity['general']['beds'] - self.ward_capacity['general']['available']:02d}"
        
        # Emergency overflow
        return 'emergency', f"ER-OVERFLOW-{uuid4().hex[:4].upper()}"
    
    async def _allocate_regular_bed(self, medical_condition: str) -> tuple[str, str]:
        """Allocate appropriate bed for regular admission."""
        # Determine ward based on medical condition
        if 'pediatric' in medical_condition.lower() or 'child' in medical_condition.lower():
            ward = 'pediatric'
        elif 'maternity' in medical_condition.lower() or 'pregnancy' in medical_condition.lower():
            ward = 'maternity'
        else:
            ward = 'general'
        
        if self.ward_capacity[ward]['available'] > 0:
            self.ward_capacity[ward]['available'] -= 1
            return ward, f"{ward.upper()}-{self.ward_capacity[ward]['beds'] - self.ward_capacity[ward]['available']:02d}"
        
        # Fallback to general ward
        if self.ward_capacity['general']['available'] > 0:
            self.ward_capacity['general']['available'] -= 1
            return 'general', f"GEN-{self.ward_capacity['general']['beds'] - self.ward_capacity['general']['available']:02d}"
        
        return 'general', f"GEN-WAIT-{uuid4().hex[:4].upper()}"
    
    async def _register_legal_case(self, patient_id: str, police_case_number: str, accident_details: Dict[str, Any]) -> bool:
        """Register legal case with police/legal system."""
        try:
            # Mock legal case registration
            legal_case_data = {
                'patient_id': patient_id,
                'police_case_number': police_case_number,
                'accident_details': accident_details,
                'registration_time': datetime.utcnow().isoformat(),
                'status': 'registered'
            }
            
            # In real implementation, this would call legal system API
            logger.info(f"Legal case registered: {legal_case_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering legal case: {e}")
            return False
    
    async def _quick_insurance_check(self, patient_info: PatientInfo) -> bool:
        """Perform quick insurance verification for emergency cases."""
        if not patient_info or not patient_info.insurance_provider:
            return False
        
        try:
            # Mock insurance verification
            provider = patient_info.insurance_provider.lower()
            if provider in self.insurance_providers:
                # In real implementation, this would call insurance API
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error in quick insurance check: {e}")
            return False
    
    async def _generate_patient_id(self, patient_info: PatientInfo) -> str:
        """Generate unique patient ID."""
        # Use patient name and DOB to generate consistent ID
        name_part = patient_info.name.replace(' ', '').upper()[:4]
        dob_part = patient_info.date_of_birth.replace('-', '')[-4:]
        unique_part = uuid4().hex[:4].upper()
        
        return f"{name_part}{dob_part}{unique_part}"
    
    async def _verify_patient_identity(self, patient_info: PatientInfo) -> bool:
        """Verify patient identity using various methods."""
        try:
            # Mock identity verification
            # In real implementation, this would check against government databases
            
            # Basic validation
            if not patient_info.name or len(patient_info.name) < 2:
                return False
            
            if not patient_info.date_of_birth:
                return False
            
            # Validate phone number format
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, patient_info.contact_number):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in identity verification: {e}")
            return False
    
    async def _process_documents(self, documents: List[str]) -> bool:
        """Process uploaded documents using OCR."""
        try:
            for doc in documents:
                # Decode base64 document
                doc_bytes = base64.b64decode(doc)
                image = Image.open(io.BytesIO(doc_bytes))
                
                # Extract text using OCR
                try:
                    import pytesseract
                    text = pytesseract.image_to_string(image)
                except ImportError:
                    text = "OCR not available - pytesseract not installed"
                
                # Process extracted text (could be used for verification)
                logger.info(f"Document processed, extracted text length: {len(text)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return False
    
    async def _verify_insurance(self, patient_info: PatientInfo) -> bool:
        """Verify insurance information."""
        if not patient_info.insurance_provider or not patient_info.insurance_number:
            return False
        
        try:
            # Mock insurance verification
            provider = patient_info.insurance_provider.lower()
            if provider in self.insurance_providers:
                # In real implementation, this would call insurance provider API
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error in insurance verification: {e}")
            return False
    
    def _estimate_stay_duration(self, medical_condition: str) -> str:
        """Estimate hospital stay duration based on medical condition."""
        condition_lower = medical_condition.lower()
        
        if any(word in condition_lower for word in ['trauma', 'surgery', 'accident']):
            return '3-7 days'
        elif any(word in condition_lower for word in ['infection', 'pneumonia']):
            return '5-10 days'
        elif any(word in condition_lower for word in ['checkup', 'routine']):
            return '1-2 days'
        else:
            return '2-5 days'
    
    async def _generate_admission_notes(self, patient_info: PatientInfo, admission_input: AdmissionInput, 
                                      ward_assigned: str, legal_case_registered: bool) -> str:
        """Generate admission notes using AI."""
        try:
            notes_prompt = f"""
            Generate admission notes for a patient with the following information:
            
            Patient: {patient_info.name if patient_info else 'Unknown'}
            Medical Condition: {admission_input.medical_condition}
            Emergency Level: {admission_input.emergency_level}
            Ward Assigned: {ward_assigned}
            Legal Case: {legal_case_registered}
            
            Generate professional admission notes including:
            - Patient presentation
            - Admission reason
            - Ward assignment rationale
            - Special considerations
            - Next steps
            """
            
            notes = await self.chain.ainvoke({"context": notes_prompt, "instructions": "Generate admission notes"})
            return notes
            
        except Exception as e:
            logger.error(f"Error generating admission notes: {e}")
            return f"Admission notes: Patient admitted to {ward_assigned} ward. {admission_input.medical_condition}"
    
    def _create_admission_prompt(self) -> PromptTemplate:
        """Create prompt template for admission processing."""
        template = """
        You are an AI admission specialist for a hospital. Your role is to:
        
        1. Extract patient information from text/voice input
        2. Generate admission notes
        3. Provide professional medical documentation
        
        Context: {context}
        
        Instructions: {instructions}
        
        Response: Provide a clear, professional response in the requested format.
        """
        
        return PromptTemplate(
            input_variables=["context", "instructions"],
            template=template
        )
    
    async def _log_admission(self, session_id: str, admission_input: AdmissionInput, admission_result: AdmissionResult):
        """Log admission process for audit and compliance."""
        log_entry = {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'patient_id': admission_result.patient_id,
            'admission_type': admission_result.admission_type,
            'ward_assigned': admission_result.ward_assigned,
            'verification_status': admission_result.verification_status,
            'legal_case': admission_input.legal_case,
            'confidence_score': admission_result.confidence_score
        }
        
        logger.info(f"Admission logged: {log_entry}")
    
    async def health_check(self) -> bool:
        """Check admission agent health."""
        try:
            # Check if LLM is accessible
            test_response = await self.chain.ainvoke({"context": "Test", "instructions": "Test"})
            return True
        except Exception as e:
            logger.error(f"Admission agent health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown admission agent."""
        logger.info("Shutting down Admission Agent")
        # Cleanup resources if needed 