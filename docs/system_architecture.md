# 🏗️ System Architecture - MediSentinel

## 📋 Architecture Overview

MediSentinel follows a microservices-based architecture with AI agents as the core components. The system is designed for high availability, scalability, and compliance with healthcare regulations.

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
│  Scheduling Agent│  Medical Records │  Communication    │  Agent Coordinator   │
│  (Python/Calendar)│  Agent (Python)  │  Agent (Python)   │  (Python/LangChain) │
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
│ Medical Records │ ← Check history & preferences
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Scheduling Agent│ ← Find available slots
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Billing Agent   │ ← Process payment & insurance
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Communication   │ ← Send confirmation
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
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medisentinel
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=medisentinel
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Production Environment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medisentinel-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: medisentinel-backend
  template:
    metadata:
      labels:
        app: medisentinel-backend
    spec:
      containers:
      - name: backend
        image: medisentinel/backend:latest
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
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(title="MediSentinel API", version="1.0.0")

# Authentication middleware
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Patient endpoints
@app.post("/patients/")
async def create_patient(patient: PatientCreate, token: str = Depends(oauth2_scheme)):
    return await patient_service.create(patient)

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str, token: str = Depends(oauth2_scheme)):
    return await patient_service.get(patient_id)

# Emergency endpoints
@app.post("/emergency/triage")
async def emergency_triage(triage_data: TriageInput):
    return await triage_agent.process(triage_data)

@app.post("/emergency/admission")
async def emergency_admission(admission_data: AdmissionInput):
    return await admission_agent.process(admission_data)

# Appointment endpoints
@app.post("/appointments/")
async def create_appointment(appointment: AppointmentCreate):
    return await scheduling_agent.book_appointment(appointment)

# Billing endpoints
@app.post("/billing/estimate")
async def estimate_billing(billing_data: BillingInput):
    return await billing_agent.estimate(billing_data)
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