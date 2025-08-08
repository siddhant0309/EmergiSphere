"""
MediSentinel Triage Agent

This agent assesses patient urgency and medical conditions from multiple
input sources including voice, text, vital signs, and visual data.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from pydantic import BaseModel
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai

from .base_agent import BaseAgent


class TriageInput(BaseModel):
    """Input data for triage assessment."""
    voice_input: Optional[str] = None
    text_input: Optional[str] = None
    vital_signs: Optional[Dict[str, Any]] = None
    visual_data: Optional[str] = None  # Base64 encoded image or description
    contextual_data: Optional[Dict[str, Any]] = None


class TriageResult(BaseModel):
    """Result of triage assessment."""
    emergency_level: str  # "critical", "urgent", "non-urgent"
    medical_condition: str
    priority_score: int  # 1-5 scale
    required_resources: List[str]
    immediate_actions: List[str]
    confidence_score: float
    reasoning: str


class TriageAgent(BaseAgent):
    """
    AI-powered triage agent for assessing patient urgency and conditions.
    
    Uses multiple input sources to determine appropriate care level and
    resource allocation.
    """
    
    def __init__(self):
        super().__init__()
        self.llm = OpenAI(temperature=0.1)
        self.triage_prompt = self._create_triage_prompt()
        self.triage_chain = LLMChain(llm=self.llm, prompt=self.triage_prompt)
        
        # Medical knowledge base for condition classification
        self.medical_conditions = {
            'trauma': ['head injury', 'gunshot', 'stab wound', 'car accident'],
            'cardiac': ['chest pain', 'heart attack', 'arrhythmia'],
            'respiratory': ['shortness of breath', 'asthma attack', 'pneumonia'],
            'neurological': ['stroke', 'seizure', 'unconsciousness'],
            'obstetric': ['labor', 'pregnancy complications'],
            'pediatric': ['child injury', 'fever', 'dehydration']
        }
    
    def _create_triage_prompt(self) -> PromptTemplate:
        """Create the prompt template for triage assessment."""
        template = """
        You are an expert emergency medicine triage nurse. Assess the following patient information and provide a triage assessment.
        
        Patient Information:
        Voice/Text Input: {voice_text_input}
        Vital Signs: {vital_signs}
        Visual Data: {visual_data}
        Contextual Data: {contextual_data}
        
        Based on this information, provide a triage assessment in the following JSON format:
        {{
            "emergency_level": "critical|urgent|non-urgent",
            "medical_condition": "specific condition or symptoms",
            "priority_score": 1-5,
            "required_resources": ["resource1", "resource2"],
            "immediate_actions": ["action1", "action2"],
            "confidence_score": 0.0-1.0,
            "reasoning": "detailed explanation of assessment"
        }}
        
        Emergency Level Guidelines:
        - Critical (Priority 1): Immediate life-threatening conditions
        - Urgent (Priority 2-3): Serious but not immediately life-threatening
        - Non-urgent (Priority 4-5): Can wait for treatment
        
        Consider:
        - Vital sign abnormalities
        - Mechanism of injury
        - Patient age and comorbidities
        - Time sensitivity of condition
        - Available resources
        
        Assessment:
        """
        
        return PromptTemplate(
            input_variables=["voice_text_input", "vital_signs", "visual_data", "contextual_data"],
            template=template
        )
    
    async def process(self, context: Any) -> Dict[str, Any]:
        """
        Process triage assessment for a patient.
        
        Args:
            context: Workflow context containing patient data
            
        Returns:
            Triage assessment results
        """
        try:
            # Extract triage input from context
            triage_input = self._extract_triage_input(context)
            
            # Perform triage assessment
            triage_result = await self._assess_patient(triage_input)
            
            # Log the assessment
            await self._log_assessment(context.session_id, triage_input, triage_result)
            
            # Update context with triage results
            return {
                'emergency_level': triage_result.emergency_level,
                'medical_condition': triage_result.medical_condition,
                'priority_score': triage_result.priority_score,
                'required_resources': triage_result.required_resources,
                'immediate_actions': triage_result.immediate_actions,
                'triage_confidence': triage_result.confidence_score,
                'triage_reasoning': triage_result.reasoning
            }
            
        except Exception as e:
            logging.error(f"Error in triage assessment: {e}")
            # Return default critical assessment in case of error
            return {
                'emergency_level': 'critical',
                'medical_condition': 'unknown',
                'priority_score': 1,
                'required_resources': ['emergency_room', 'doctor'],
                'immediate_actions': ['immediate_medical_attention'],
                'triage_confidence': 0.0,
                'triage_reasoning': f'Error in assessment: {str(e)}'
            }
    
    def _extract_triage_input(self, context: Any) -> TriageInput:
        """Extract triage input data from workflow context."""
        metadata = context.metadata
        
        return TriageInput(
            voice_input=metadata.get('voice_input'),
            text_input=metadata.get('text_input'),
            vital_signs=metadata.get('vital_signs'),
            visual_data=metadata.get('visual_data'),
            contextual_data=metadata.get('contextual_data', {})
        )
    
    async def _assess_patient(self, triage_input: TriageInput) -> TriageResult:
        """
        Assess patient using AI and medical knowledge.
        
        Args:
            triage_input: Patient input data
            
        Returns:
            Triage assessment result
        """
        # Prepare input for LLM
        voice_text_input = triage_input.voice_input or triage_input.text_input or "No input provided"
        vital_signs_str = self._format_vital_signs(triage_input.vital_signs)
        visual_data_str = triage_input.visual_data or "No visual data"
        contextual_data_str = self._format_contextual_data(triage_input.contextual_data)
        
        # Get AI assessment
        llm_response = await self.triage_chain.arun(
            voice_text_input=voice_text_input,
            vital_signs=vital_signs_str,
            visual_data=visual_data_str,
            contextual_data=contextual_data_str
        )
        
        # Parse LLM response
        triage_result = self._parse_llm_response(llm_response)
        
        # Validate and enhance with medical knowledge
        triage_result = await self._enhance_with_medical_knowledge(triage_input, triage_result)
        
        return triage_result
    
    def _format_vital_signs(self, vital_signs: Optional[Dict[str, Any]]) -> str:
        """Format vital signs for LLM input."""
        if not vital_signs:
            return "No vital signs available"
        
        formatted = []
        for key, value in vital_signs.items():
            formatted.append(f"{key}: {value}")
        
        return ", ".join(formatted)
    
    def _format_contextual_data(self, contextual_data: Optional[Dict[str, Any]]) -> str:
        """Format contextual data for LLM input."""
        if not contextual_data:
            return "No contextual data available"
        
        formatted = []
        for key, value in contextual_data.items():
            formatted.append(f"{key}: {value}")
        
        return ", ".join(formatted)
    
    def _parse_llm_response(self, response: str) -> TriageResult:
        """Parse LLM response into structured triage result."""
        try:
            # Extract JSON from response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback parsing
                data = self._fallback_parse(response)
            
            return TriageResult(
                emergency_level=data.get('emergency_level', 'urgent'),
                medical_condition=data.get('medical_condition', 'unknown'),
                priority_score=data.get('priority_score', 3),
                required_resources=data.get('required_resources', []),
                immediate_actions=data.get('immediate_actions', []),
                confidence_score=data.get('confidence_score', 0.5),
                reasoning=data.get('reasoning', 'Assessment completed')
            )
            
        except Exception as e:
            logging.error(f"Error parsing LLM response: {e}")
            return self._create_default_result()
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails."""
        # Simple keyword-based parsing
        response_lower = response.lower()
        
        emergency_level = 'urgent'
        if any(word in response_lower for word in ['critical', 'emergency', 'immediate']):
            emergency_level = 'critical'
        elif any(word in response_lower for word in ['stable', 'routine', 'non-urgent']):
            emergency_level = 'non-urgent'
        
        return {
            'emergency_level': emergency_level,
            'medical_condition': 'unknown',
            'priority_score': 3,
            'required_resources': ['medical_attention'],
            'immediate_actions': ['assess_patient'],
            'confidence_score': 0.3,
            'reasoning': 'Fallback assessment due to parsing error'
        }
    
    def _create_default_result(self) -> TriageResult:
        """Create a default triage result for error cases."""
        return TriageResult(
            emergency_level='urgent',
            medical_condition='unknown',
            priority_score=3,
            required_resources=['medical_attention'],
            immediate_actions=['assess_patient'],
            confidence_score=0.0,
            reasoning='Default assessment due to processing error'
        )
    
    async def _enhance_with_medical_knowledge(
        self, 
        triage_input: TriageInput, 
        triage_result: TriageResult
    ) -> TriageResult:
        """
        Enhance AI assessment with medical knowledge and rules.
        
        Args:
            triage_input: Original input data
            triage_result: AI assessment result
            
        Returns:
            Enhanced triage result
        """
        # Check vital signs for critical values
        if triage_input.vital_signs:
            enhanced_result = self._check_vital_signs(triage_input.vital_signs, triage_result)
            if enhanced_result:
                return enhanced_result
        
        # Check for specific medical conditions
        condition_enhancement = self._check_medical_conditions(triage_input, triage_result)
        if condition_enhancement:
            return condition_enhancement
        
        return triage_result
    
    def _check_vital_signs(self, vital_signs: Dict[str, Any], triage_result: TriageResult) -> Optional[TriageResult]:
        """Check vital signs for critical values that override AI assessment."""
        critical_findings = []
        
        # Blood pressure
        if 'systolic' in vital_signs and vital_signs['systolic'] < 90:
            critical_findings.append('hypotension')
        
        if 'diastolic' in vital_signs and vital_signs['diastolic'] > 120:
            critical_findings.append('hypertension')
        
        # Heart rate
        if 'heart_rate' in vital_signs:
            hr = vital_signs['heart_rate']
            if hr < 50 or hr > 120:
                critical_findings.append('abnormal_heart_rate')
        
        # Oxygen saturation
        if 'oxygen_saturation' in vital_signs and vital_signs['oxygen_saturation'] < 90:
            critical_findings.append('hypoxemia')
        
        # Temperature
        if 'temperature' in vital_signs:
            temp = vital_signs['temperature']
            if temp > 39.0 or temp < 35.0:
                critical_findings.append('abnormal_temperature')
        
        if critical_findings:
            return TriageResult(
                emergency_level='critical',
                medical_condition=f"Critical vital signs: {', '.join(critical_findings)}",
                priority_score=1,
                required_resources=['emergency_room', 'monitoring', 'doctor'],
                immediate_actions=['immediate_medical_attention', 'vital_signs_monitoring'],
                confidence_score=0.9,
                reasoning=f"Critical vital signs detected: {', '.join(critical_findings)}"
            )
        
        return None
    
    def _check_medical_conditions(
        self, 
        triage_input: TriageInput, 
        triage_result: TriageResult
    ) -> Optional[TriageResult]:
        """Check for specific medical conditions that require immediate attention."""
        input_text = (triage_input.voice_input or triage_input.text_input or "").lower()
        
        # Check for trauma indicators
        trauma_keywords = ['gunshot', 'stab', 'car accident', 'head injury', 'unconscious']
        if any(keyword in input_text for keyword in trauma_keywords):
            return TriageResult(
                emergency_level='critical',
                medical_condition='trauma',
                priority_score=1,
                required_resources=['trauma_team', 'emergency_room', 'imaging'],
                immediate_actions=['trauma_assessment', 'stabilization'],
                confidence_score=0.8,
                reasoning='Trauma indicators detected in patient description'
            )
        
        # Check for cardiac symptoms
        cardiac_keywords = ['chest pain', 'heart attack', 'cardiac']
        if any(keyword in input_text for keyword in cardiac_keywords):
            return TriageResult(
                emergency_level='critical',
                medical_condition='cardiac',
                priority_score=1,
                required_resources=['cardiac_monitoring', 'emergency_room', 'cardiologist'],
                immediate_actions=['ecg', 'cardiac_assessment'],
                confidence_score=0.8,
                reasoning='Cardiac symptoms detected'
            )
        
        return None
    
    async def _log_assessment(
        self, 
        session_id: str, 
        triage_input: TriageInput, 
        triage_result: TriageResult
    ):
        """Log triage assessment for audit and compliance."""
        log_entry = {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'input_data': triage_input.dict(),
            'assessment_result': triage_result.dict(),
            'agent': 'triage'
        }
        
        logging.info(f"Triage assessment logged: {log_entry}")
        
        # Store in database for audit trail
        # await self._store_audit_log(log_entry)
    
    async def emergency_process(self, context: Any, override_data: Dict[str, Any]):
        """Handle emergency override processing."""
        # For emergency cases, immediately classify as critical
        return {
            'emergency_level': 'critical',
            'medical_condition': 'emergency_override',
            'priority_score': 1,
            'required_resources': ['emergency_room', 'doctor'],
            'immediate_actions': ['immediate_medical_attention'],
            'triage_confidence': 1.0,
            'triage_reasoning': 'Emergency override activated'
        }
    
    async def health_check(self) -> bool:
        """Check if the triage agent is healthy."""
        try:
            # Test LLM connectivity
            test_response = await self.triage_chain.arun(
                voice_text_input="test",
                vital_signs="test",
                visual_data="test",
                contextual_data="test"
            )
            return bool(test_response)
        except Exception as e:
            logging.error(f"Triage agent health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the triage agent."""
        logging.info("Shutting down Triage Agent")
        # Cleanup resources if needed 