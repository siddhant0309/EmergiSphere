# 🚑 EmergiSphere: Agentic AI for Emergency-First Hospital Automation

## 🎯 Project Overview

EmergiSphere is a multi-agent AI system that automates emergency hospital workflows by intelligently coordinating patient intake, billing, legal communication, and medical record management. The system uses autonomous AI agents to handle complex hospital operations, reducing manual paperwork and improving emergency response times.

## 🧠 Core Features

- **Emergency Patient Intake**: Automated registration and admission for emergency cases
- **Intelligent Triage**: AI-powered urgency assessment from multiple input sources
- **Legal Integration**: Automatic police/legal system communication for accident/crime cases
- **Paperless Billing**: Automated insurance validation and billing processes
- **Smart Scheduling**: AI-driven appointment booking and follow-up management
- **Real-time Communication**: Automated notifications to family, staff, and authorities
- **Smart Health Device Integration**: Medical reports on smartwatches, doctor scanning, emergency contact notification

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  Patient Portal  │  Staff Dashboard  │  Mobile App Interface   │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                           │
├─────────────────────────────────────────────────────────────────┤
│  Triage Agent   │  Admission Agent  │  Billing Agent           │
│  Legal Agent    │  Scheduling Agent │  Medical Records Agent   │
│  Communication Agent│  Smart Health Device Agent                │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    API & Integration Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  Voice APIs     │  EHR APIs       │  Legal System APIs        │
│  Billing APIs   │  Insurance APIs │  Communication APIs       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    Data & Storage Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL     │  FHIR Server    │  Audit Logs               │
│  MongoDB        │  File Storage   │  Compliance Database      │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Redis (for caching)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd EmergiSphere
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Initialize database**
```bash
python scripts/init_db.py
```

5. **Start the application**
```bash
python app.py
```

6. **Start Smart Health Device API (optional)**
```bash
python smart_health_api.py
```

7. **Run Smart Health Device Demo**
```bash
python smart_health_demo.py
```

## 📁 Project Structure

```
EmergiSphere/
├── agents/                 # AI Agent implementations
│   ├── triage_agent.py
│   ├── admission_agent.py
│   ├── billing_agent.py
│   ├── legal_agent.py
│   ├── scheduling_agent.py
│   ├── medical_records_agent.py
│   ├── communication_agent.py
│   └── smart_health_device_agent.py
├── api/                   # REST API endpoints
│   ├── routes/
│   └── middleware/
├── frontend/              # Web interface
│   ├── patient_portal/
│   └── staff_dashboard/
├── integrations/          # External API integrations
│   ├── ehr/
│   ├── legal/
│   ├── billing/
│   └── communication/
├── models/                # Data models
├── services/              # Business logic
├── utils/                 # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
└── scripts/               # Setup and utility scripts
```

## 🏥 Smart Health Device Features

### Key Capabilities
- **Medical Report Storage**: Secure storage of lab results, prescriptions, and medical reports on smartwatches
- **Doctor Device Scanning**: QR code/NFC scanning for immediate patient information access
- **Emergency Contact Management**: Automated notification system for family and healthcare providers
- **Vital Signs Monitoring**: Continuous monitoring with automatic emergency detection
- **Emergency Response**: Automatic activation when critical health thresholds are exceeded

### Smart Health Device API
The system includes a dedicated API for smart health device operations:
- Device registration and management
- Medical report storage and retrieval
- Vital signs monitoring and emergency detection
- Emergency contact notification
- Doctor device scanning and access control

### Getting Started with Smart Health Devices
```bash
# Start the Smart Health Device API
python smart_health_api.py

# Access API documentation
http://localhost:8001/docs

# Run demonstration
python smart_health_demo.py
```

For detailed documentation, see [Smart Health Device Integration](docs/smart_health_device_integration.md).

## 🔧 Configuration
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/emergisphere

# External APIs
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
STRIPE_SECRET_KEY=your_stripe_key

# Legal System Integration
POLICE_API_ENDPOINT=https://api.police.gov/emergency
LEGAL_SYSTEM_API_KEY=your_legal_api_key

# Hospital Configuration
HOSPITAL_ID=your_hospital_id
EMERGENCY_DEPARTMENT_ID=your_ed_id
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/agents/
pytest tests/api/
pytest tests/integrations/
```

## 📊 Monitoring & Logging

The system includes comprehensive logging and monitoring:
- Agent decision logs
- API call tracking
- Performance metrics
- Error monitoring
- Compliance audit trails

## 🔒 Security & Compliance

- HIPAA/GDPR compliant data handling
- End-to-end encryption
- Role-based access control
- Audit trail for all operations
- Secure API authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs`

---

**Built with ❤️ for better healthcare automation** 