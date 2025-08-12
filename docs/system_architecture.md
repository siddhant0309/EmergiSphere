# 🏗️ System Architecture - EmergiSphere

## 📋 Architecture Overview

EmergiSphere follows a microservices-based architecture with AI agents as the core components. The system is designed for high availability, scalability, and compliance with healthcare regulations, focusing on emergency-first hospital automation.

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Frontend Layer                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Patient Portal  │  Staff Dashboard  │  Mobile App  │  Emergency Interface     │
│  (React/Next.js) │  (React/Admin)    │  (React Native)│  (Voice/Text)          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API Gateway Layer                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Authentication  │  Rate Limiting  │  Load Balancing  │  Request Routing      │
│  (JWT/OAuth2)    │  (Redis)        │  (Nginx)         │  (Kong/AWS ALB)       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Agent Orchestrator                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Workflow Engine  │  Agent Manager  │  State Management  │  Error Handling     │
│  (LangChain)      │  (CrewAI)       │  (Redis)           │  (Circuit Breaker)  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AI Agents Layer                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Triage Agent    │  Admission Agent │  Billing Agent    │  Legal Agent         │
│  (Python/LLM)    │  (Python/OCR)    │  (Python/Stripe)  │  (Python/APIs)      │
│                                                                                 │
│  Scheduling Agent│  Medical Records │  Communication    │  Smart Health Device │
│  (Python/Calendar)│  Agent (Python)  │  Agent (Python)   │  Agent (Python)     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Integration Layer                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Voice APIs      │  EHR APIs        │  Legal APIs       │  Billing APIs       │
│  (Whisper)       │  (FHIR/HL7)      │  (Police/Court)   │  (Stripe/Insurance) │
│                                                                                 │
│  Communication   │  Insurance APIs  │  Payment APIs     │  Notification APIs  │
│  APIs (Twilio)   │  (Real-time)     │  (Stripe/PayPal)  │  (SendGrid/Push)    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Layer                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL      │  MongoDB         │  Redis Cache      │  File Storage        │
│  (Patient Data)  │  (Documents)     │  (Session/State)  │  (S3/MinIO)          │
│                                                                                 │
│  FHIR Server     │  Audit Logs      │  Compliance DB    │  Analytics DB        │
│  (Health Records)│  (ELK Stack)     │  (HIPAA/GDPR)     │  (ClickHouse)        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Technical Stack

### Frontend Technologies
- **Patient Portal**: React 18 + Next.js 14 + TypeScript
- **Staff Dashboard**: React Admin + Material-UI + Redux Toolkit
- **Mobile App**: React Native + Expo + TypeScript
- **Emergency Interface**: Voice.js + WebRTC + WebSocket

### Backend Technologies
- **API Framework**: FastAPI + Python 3.11
- **Agent Framework**: LangChain + CrewAI + AutoGen
- **LLM Integration**: OpenAI GPT-4o + Anthropic Claude
- **Database ORM**: SQLAlchemy + Alembic

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (production) / Docker Swarm (staging)
- **Cloud Platform**: AWS EKS / Azure AKS / GCP GKE
- **CI/CD**: GitHub Actions + ArgoCD

## 🔄 Data Flow Architecture

### 1. Emergency Patient Intake Flow

```
Emergency Input (Voice/Text/Photo)
         │
         ▼
┌─────────────────┐
│  API Gateway    │ ← Authentication & Rate Limiting
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Agent Orchestrator │ ← Route to appropriate agents
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Triage Agent   │ ← Assess urgency & condition
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Admission Agent │ ← Register patient & verify ID
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Legal Liaison   │ ← Check legal implications
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Medical Records │ ← Retrieve history & allergies
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Smart Health    │ ← Access device data & vitals
│ Device Agent    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Billing Agent   │ ← Estimate costs & insurance
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Communication   │ ← Notify family & staff
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Scheduling Agent│ ← Book follow-ups & specialists
└─────────────────┘
```

### 2. Regular Appointment Flow

```
Appointment Request
         │
         ▼
┌─────────────────┐
│ Admission Agent │ ← Verify patient & insurance
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Triage Agent   │ ← Assess patient condition
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Medical Records │ ← Check history & preferences
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Smart Health    │ ← Access device data
│ Device Agent    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Billing Agent   │ ← Process payment & insurance
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Scheduling Agent│ ← Find available slots
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Communication   │ ← Send confirmation
└─────────────────┘
```

### 3. Smart Health Device Flow

```
Device Scan/Registration
         │
         ▼
┌─────────────────┐
│ Smart Health    │ ← Device authentication
│ Device Agent    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Medical Records │ ← Store/retrieve reports
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Communication   │ ← Emergency notifications
└─────────────────┘
```

## 🗄️ Database Architecture

### PostgreSQL Schema (Core Data)

```sql
-- Patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    national_health_id VARCHAR(50) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    emergency_contacts JSONB,
    insurance_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Appointments table
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    doctor_id UUID REFERENCES doctors(id),
    appointment_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'scheduled',
    scheduled_at TIMESTAMP,
    duration_minutes INTEGER DEFAULT 30,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Medical records table
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    visit_date TIMESTAMP,
    symptoms TEXT,
    diagnosis TEXT,
    treatment TEXT,
    medications JSONB,
    vital_signs JSONB,
    created_by UUID REFERENCES doctors(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Billing table
CREATE TABLE billing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    appointment_id UUID REFERENCES appointments(id),
    amount DECIMAL(10,2),
    insurance_coverage DECIMAL(10,2),
    patient_responsibility DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### MongoDB Collections (Documents & Analytics)

```javascript
// Legal cases collection
{
  _id: ObjectId,
  patient_id: String,
  case_type: String, // "accident", "crime", "domestic_violence"
  incident_date: Date,
  police_report: String,
  evidence: [String], // URLs to stored files
  status: String,
  legal_actions: [{
    action: String,
    date: Date,
    outcome: String
  }],
  created_at: Date
}

// Agent logs collection
{
  _id: ObjectId,
  agent_name: String,
  session_id: String,
  input_data: Object,
  output_data: Object,
  processing_time: Number,
  success: Boolean,
  error_message: String,
  timestamp: Date
}

// Communication logs collection
{
  _id: ObjectId,
  patient_id: String,
  communication_type: String, // "sms", "email", "call"
  recipient: String,
  message: String,
  status: String,
  sent_at: Date,
  delivered_at: Date
}

// Smart device data collection
{
  _id: ObjectId,
  device_id: String,
  patient_id: String,
  device_type: String,
  vital_signs: Object,
  medical_reports: [Object],
  emergency_contacts: [Object],
  last_sync: Date,
  battery_level: Number,
  is_connected: Boolean
}
```

## 🔐 Security Architecture

### Authentication & Authorization

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OAuth 2.0     │    │   JWT Tokens    │    │   Role-Based    │
│   Provider      │───▶│   (Access/      │───▶│   Access        │
│   (Azure AD)    │    │    Refresh)     │    │   Control       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Multi-Factor  │    │   Token         │    │   Permission    │
│   Authentication │    │   Validation    │    │   Matrix        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Encryption

- **At Rest**: AES-256 encryption for all databases
- **In Transit**: TLS 1.3 for all API communications
- **End-to-End**: PGP encryption for sensitive medical data
- **Key Management**: AWS KMS / Azure Key Vault

## 📊 Monitoring & Observability

### Logging Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   Log           │    │   Elasticsearch │
│   Logs          │───▶│   Aggregator    │───▶│   (Search &     │
│   (JSON)        │    │   (Fluentd)     │    │    Analytics)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent         │    │   Metrics       │    │   Grafana       │
│   Decision      │    │   Collector     │    │   (Dashboards)  │
│   Logs          │    │   (Prometheus)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Health Checks & Alerting

- **Application Health**: Kubernetes liveness/readiness probes
- **Agent Health**: Custom health check endpoints
- **Database Health**: Connection pool monitoring
- **API Health**: Response time and error rate monitoring
- **Alerting**: PagerDuty integration for critical issues

## 🚀 Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml
version: '3.8'
services:
  # Main application
  medisentinel:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://medisentinel:password@db:5432/medisentinel
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
      
  # PostgreSQL database
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=medisentinel
      - POSTGRES_USER=medisentinel
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
      
  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
      
  # MongoDB for document storage
  mongodb:
    image: mongo:6
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
      - MONGO_INITDB_DATABASE=medisentinel
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped
      
  # Elasticsearch for logging and search
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    restart: unless-stopped
      
  # Kibana for log visualization
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped
      
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
      
  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped
```

### Production Environment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: emergisphere-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: emergisphere-backend
  template:
    metadata:
      labels:
        app: emergisphere-backend
    spec:
      containers:
      - name: backend
        image: emergisphere/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 🔄 API Architecture

### RESTful API Design

```python
# FastAPI application structure
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer

app = FastAPI(title="EmergiSphere API", version="1.0.0")

# Authentication middleware
oauth2_scheme = HTTPBearer()

# Health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EmergiSphere", "version": "1.0.0"}

@app.get("/health/agents")
async def agent_health_check(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_agent_health()

# Emergency workflow endpoints
@app.post("/emergency/triage")
async def emergency_triage(emergency_input: EmergencyInput):
    return await orchestrator.start_workflow("emergency", emergency_input.dict())

@app.post("/emergency/override/{session_id}")
async def emergency_override(session_id: str, override_data: Dict[str, Any]):
    return await orchestrator.emergency_override(session_id, override_data)

# Regular appointment endpoints
@app.post("/appointments/schedule")
async def schedule_appointment(appointment_input: AppointmentInput):
    return await orchestrator.start_workflow("regular", appointment_input.dict())

# Workflow management endpoints
@app.get("/workflow/{session_id}")
async def get_workflow_status(session_id: str):
    return await orchestrator.get_workflow_status(session_id)

@app.post("/workflow/{session_id}/complete")
async def complete_workflow(session_id: str):
    return await orchestrator.complete_workflow(session_id)
```

### Smart Health Device API

```python
# Smart Health Device API endpoints
@app.post("/devices/register")
async def register_device(request: DeviceRegistrationRequest):
    return await smart_device_agent.register_device(request)

@app.post("/devices/scan")
async def scan_device(request: DeviceScanRequest):
    return await smart_device_agent.scan_device(request)

@app.post("/devices/{device_id}/reports")
async def store_medical_report(device_id: str, request: MedicalReportRequest):
    return await smart_device_agent.store_medical_report(request)

@app.get("/devices/{device_id}/vital-signs")
async def get_vital_signs(device_id: str):
    return await smart_device_agent.get_vital_signs(device_id)

@app.post("/devices/{device_id}/emergency-check")
async def check_emergency_conditions(device_id: str):
    return await smart_device_agent.check_emergency_conditions(device_id)
```

### WebSocket API for Real-time Updates

```python
@app.websocket("/ws/patient/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    await websocket.accept()
    try:
        while True:
            # Send real-time updates to family/staff
            updates = await get_patient_updates(patient_id)
            await websocket.send_json(updates)
            await asyncio.sleep(30)  # Update every 30 seconds
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for patient {patient_id}")
```

## 🤖 Agent Architecture

### Base Agent Class

```python
class BaseAgent(ABC):
    """Base class for all EmergiSphere AI agents."""
    
    def __init__(self):
        self.agent_name = self.__class__.__name__
        self.logger = logging.getLogger(f"agent.{self.agent_name.lower()}")
        self.is_healthy = True
        self.last_health_check = datetime.utcnow()
    
    @abstractmethod
    async def process(self, context: Any) -> Dict[str, Any]:
        """Process the main agent logic."""
        pass
    
    async def health_check(self) -> bool:
        """Check if the agent is healthy."""
        pass
    
    async def emergency_process(self, context: Any, override_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency processing when normal workflow is bypassed."""
        pass
    
    async def shutdown(self):
        """Gracefully shutdown the agent."""
        pass
```

### Agent Orchestrator

```python
class AgentOrchestrator:
    """Central coordinator for all EmergiSphere AI agents."""
    
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
                'triage', 'admission', 'legal', 'medical_records',
                'smart_health_device', 'billing', 'communication', 'scheduling'
            ],
            'regular': [
                'admission', 'triage', 'medical_records', 'smart_health_device',
                'billing', 'scheduling', 'communication'
            ],
            'device_scan': [
                'smart_health_device', 'medical_records', 'communication'
            ],
            'emergency_device': [
                'smart_health_device', 'triage', 'communication', 'admission'
            ]
        }
```

## 📈 Scalability Considerations

### Horizontal Scaling
- **Stateless Services**: All backend services are stateless for easy scaling
- **Database Sharding**: Patient data sharded by geographic region
- **Load Balancing**: Round-robin load balancing with health checks
- **Auto-scaling**: Kubernetes HPA based on CPU/memory usage

### Performance Optimization
- **Caching**: Redis for session data and frequently accessed information
- **CDN**: CloudFront for static assets and global content delivery
- **Database Optimization**: Connection pooling, query optimization, indexing
- **Async Processing**: Celery for background tasks and agent processing

### Disaster Recovery
- **Multi-Region Deployment**: Active-active deployment across regions
- **Data Backup**: Automated daily backups with point-in-time recovery
- **Failover**: Automatic failover to secondary region
- **Monitoring**: Comprehensive monitoring and alerting for all components 