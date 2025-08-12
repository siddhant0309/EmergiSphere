from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import types

sys.modules.setdefault("langchain", types.ModuleType("langchain"))
sys.modules.setdefault("langchain.agents", types.ModuleType("langchain.agents"))
sys.modules.setdefault("langchain.schema", types.ModuleType("langchain.schema"))
sys.modules["langchain.agents"].AgentExecutor = object
sys.modules["langchain.schema"].BaseMessage = object

sys.modules.setdefault("crewai", types.ModuleType("crewai"))
sys.modules["crewai"].Crew = object
sys.modules["crewai"].Process = object

# Stub agent modules to avoid heavy dependencies
def _stub_agent_module(module_name, class_name):
    mod = types.ModuleType(module_name)
    stub_cls = type(class_name, (), {
        "__init__": lambda self, *args, **kwargs: None,
        "process": lambda self, context: {},
        "emergency_process": lambda self, context, data: None,
        "health_check": lambda self: True,
        "shutdown": lambda self: None,
    })
    setattr(mod, class_name, stub_cls)
    sys.modules[module_name] = mod

_stub_agent_module("agents.triage_agent", "TriageAgent")
_stub_agent_module("agents.admission_agent", "AdmissionAgent")
_stub_agent_module("agents.billing_agent", "BillingAgent")
_stub_agent_module("agents.legal_agent", "LegalAgent")
_stub_agent_module("agents.scheduling_agent", "SchedulingAgent")
_stub_agent_module("agents.medical_records_agent", "MedicalRecordsAgent")
_stub_agent_module("agents.communication_agent", "CommunicationAgent")

from agents.orchestrator import WorkflowContext

def test_metadata_isolation():
    c1 = WorkflowContext(
        session_id="1",
        workflow_type="emergency",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    c2 = WorkflowContext(
        session_id="2",
        workflow_type="regular",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    c1.metadata["key"] = "value"

    assert c2.metadata == {}
