# Hospital Intelligence System - AI-Powered Resource Management

A conversational AI system that enables hospital administrators to query complex databases using natural language. Built with Google's Agent Development Kit (ADK) and multi-agent architecture, it transforms everyday questions into SQL queries and delivers insights instantly.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Google API Key (Gemini)

### Setup
```bash
# Clone repository
git clone https://github.com/manyaababbar/froncort.git
cd froncort

# Create .env file with the following content:
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
DB_USER=hospital_user
DB_PASSWORD=hospital_pass
DB_HOST=db
DB_PORT=3306
DB_NAME=hospital_data
DATABASE_URL=sqlite:///./my_chatbot_data.db
VITE_REACT_APP_FASTAPI_URL=http://localhost:8000
DEBUG=true

# Start services
docker-compose up -d --build
```

Access the application:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Problem Statement

### The Challenge
Healthcare facilities struggle with three fundamental problems:

1. **Data Accessibility Barrier** - Critical information trapped in complex SQL databases
2. **Time-Sensitive Operations** - Emergency resource allocation requires instant data access
3. **Technical Knowledge Gap** - Non-technical staff cannot leverage database insights

### Our Solution
An intelligent agent system that bridges human language and database queries, democratizing access to hospital data across all staff levels—from administrators to medical professionals.

**Key Capabilities:**
1. **Natural Language Processing** - Ask questions like "Which hospitals need more ICU beds?" instead of writing complex SQL
2. **Automated SQL Generation** - Analyzes database schema and creates optimized queries with proper joins
3. **Result Validation** - Ensures query results match user intent before responding
4. **Context Awareness** - Remembers conversation history for follow-up questions
5. **Human-Friendly Responses** - Delivers insights in natural language, not raw data dumps

**Example Workflow:**
```
User Input: "Which hospitals have oxygen below 5000 liters?"
        ↓
Schema Analysis → Query Refinement → SQL Generation
        ↓
Query Execution → Result Validation
        ↓
Natural Response: "3 hospitals have low oxygen: Ruby Hill Hospital (2,768L), 
                   Pune NMC Hospital (3,743L), Narhe Hospital (2,370L)"
```

**Measurable Impact:**
- ⚡ Response time: **5 minutes → 5 seconds**
- 👥 User accessibility: **IT specialists only → All staff**
- ✓ Query accuracy: **Manual errors eliminated**
- 📊 Data coverage: **50+ hospitals managed seamlessly**

---

## Database Architecture

### Hospital Data Model

MySQL database containing realistic operational data for **50 hospitals across Pune, Maharashtra**.

**Data Generation:** Synthetically created using Python (NumPy/Pandas) with seed 7777 for reproducibility
- Hospital distribution: Small (45%), Medium (40%), Large (15%)
- Ownership types: Government (55%), Private (40%), Trust (5%)
- Realistic statistical distributions (not all facilities at maximum capacity)

### Core Tables

#### 1. **hospitals** - Facility master records
```sql
hospital_id (PK), hospital_name, region, latitude, longitude,
ownership_type, max_capacity_beds, ward_capacity_beds
```
*Contains 50 hospitals with geographic coordinates within Pune boundaries, capacity ranging 25-800 beds*

#### 2. **hospital_resource_timeseries** - Live operational metrics
```sql
timestamp, hospital_id (FK), occupied_beds, total_beds, icu_beds,
icu_occupied, ventilators, in_use_ventilators, available_oxygen_liters,
doctors_on_shift, doctors_required, nurses, ambulance_arrivals,
critical_cases, ed_turnaround_time, ...
```
*Tracks 25+ real-time metrics: bed utilization, equipment status, staffing levels, patient flow*

#### 3. **hospital_finance_monthly** - Budget and expenditure tracking
```sql
hospital_id (FK), period, total_expenditure, operational_expenditure,
staff_cost, supply_cost, revenue, budget_allocated, budget_remaining
```
*Monthly expenditure ranges: ₹1M-₹9M per hospital, staff costs represent 50-70% of total spending*

#### 4. **suppliers** - Vendor management
```sql
vendor_id (PK), vendor_name, vendor_type, contact (JSON),
lead_time_days, payment_terms_days
```
*Three vendor categories: Oxygen suppliers, Equipment vendors, Diagnostic services*

#### 5. **inventory_items** - Supply catalog
```sql
item_id (PK), item_name, unit, reorder_level, reorder_qty,
unit_cost, asset_flag
```
*Critical items tracked: Oxygen cylinders (liters), Ventilators (units), PPE supplies*

**Data Realism Features:**
- Normal distributions for occupancy rates (avoiding unrealistic 100% values)
- Accurate Pune geographic coordinates (latitude/longitude)
- Staffing shortages reflected (doctors_required > doctors_on_shift)
- Financial ratios aligned with healthcare industry standards

---

## Multi-Agent System Architecture

### Agent Orchestration Model
```
┌──────────────────────────────────────┐
│  Root SQL Agent (Gemini 2.5 Flash)  │ ← Central Orchestrator
│  - Workflow coordination             │
│  - SQL query generation              │
│  - Natural language response         │
└────┬─────────────────────────────────┘
     │
     ├────────┬──────────┬─────────────┐
     ▼        ▼          ▼             ▼
get_schema  run_sql   rewrite_      evaluate_
   _tool    _query_   prompt_       result_
[Function]  tool      agent         agent
           [Function] [Sub-Agent]   [Sub-Agent]
```

### Agent Components

#### 1. **Root SQL Agent** (`sql_agent/agent.py`)
**Primary Role:** Orchestrates the entire query processing pipeline

Responsibilities:
- Coordinates function tools and sub-agents
- Generates SQL queries from refined natural language
- Converts database results into conversational responses
- Manages session state using SQLite persistence

**Model:** Gemini 2.5 Flash (optimized for speed and quality balance)

#### 2. **Query Rewrite Agent** (`subagents/rewrite_prompt.py`)
**Primary Role:** Query clarification and standardization

Responsibilities:
- Transforms vague questions into precise database queries
- Maps colloquial language to actual database column names
- Resolves context from previous conversation turns

**Example Transformation:**
```
Original Query: "Show me busy hospitals"
Refined Query:  "List hospitals where current bed occupancy exceeds 80% of total capacity"
```

#### 3. **Result Evaluation Agent** (`subagents/evaluate_result.py`)
**Primary Role:** Quality assurance validation

Responsibilities:
- Compares query results against original user intent
- Returns evaluation status: "Correct" or "Partial"
- Triggers query regeneration if results don't satisfy the question

#### 4. **Function Tools** (`functions/db_tools.py`)

**get_schema_tool** - Database structure retrieval
- Returns table schemas and column definitions
- Provides relationship information for joins
- Uses LangChain's SQLDatabase utility

**run_sql_query_tool** - Safe query execution
- Executes generated SQL against MySQL database
- Returns structured results
- Implements error handling and timeout protection

### Design Philosophy

**Why Multi-Agent Architecture?**
1. **Separation of Concerns** - Each component handles a single, well-defined responsibility
2. **Modularity** - Agents can be developed, tested, and deployed independently
3. **Reduced Complexity** - Specialized agents excel at focused tasks vs. monolithic systems
4. **Fault Isolation** - Individual agent failures don't cascade to entire system

**Technology Stack Rationale:**
- **Gemini 2.5 Flash** - Optimal balance of inference speed and response quality
- **LangChain** - Industry-standard database abstraction utilities
- **SQLite** - Lightweight session persistence (Google ADK DatabaseSessionService)
- **FastAPI** - Modern async Python web framework
- **React + Vite** - Fast development and production builds for frontend

---

## Intelligent Query Processing

### Complete Execution Flow

**User Question:** *"Which hospitals need additional doctors?"*

**Step 1: Database Schema Retrieval**
```python
get_schema_tool()
# Returns: Table structures, column definitions, foreign key relationships
```

**Step 2: Query Refinement**
```python
rewrite_prompt_agent()
# Input:  "Which hospitals need additional doctors?"
# Output: "Identify hospitals where doctors_required exceeds doctors_on_shift 
#          in the hospital_resource_timeseries table"
```

**Step 3: SQL Query Generation** (Root Agent)
```sql
SELECT 
    h.hospital_name,
    hr.doctors_on_shift,
    hr.doctors_required,
    (hr.doctors_required - hr.doctors_on_shift) AS shortage
FROM hospitals h
JOIN hospital_resource_timeseries hr 
    ON h.hospital_id = hr.hospital_id
WHERE hr.doctors_required > hr.doctors_on_shift
ORDER BY shortage DESC;
```

**Step 4: Query Execution**
```python
run_sql_query_tool()
# Executes SQL, returns structured results
```

**Step 5: Result Validation**
```python
evaluate_result_agent()
# Verifies: Does output answer the original question?
# Status: "Correct" ✓
```

**Step 6: Natural Language Response**
```
"Currently, 12 hospitals have doctor shortages:
- Kothrud Medical Center: 8 doctors short
- Baner Health Facility: 5 doctors short  
- Wakad Hospital: 4 doctors short
..."
```

---

## Conversational Memory & Session Management

### Context Retention System

The system maintains conversation history using SQLite-based session storage, enabling multi-turn dialogues:

**Example Conversation Flow:**
```
User: "Show me hospitals with available ICU beds"
System: [Stores query + results in SQLite]
        "15 hospitals currently have ICU availability..."

User: "What about their oxygen levels?"
System: [Retrieves session → understands "their" refers to those 15 hospitals]
        "Among those 15 hospitals, oxygen levels range from 3,200 to 8,900 liters..."
```

### Robust Session Management

**SQLite-Based Persistence:**
- Full conversation history stored in `my_chatbot_data.db`
- Enables follow-up questions without context loss
- Supports cross-session memory for returning users

**Session Lifecycle Implementation:**

**1. Creation with Exponential Backoff**
```python
async def ensure_session_with_retries(max_retries=5):
    # Retry delays: 0.1s → 0.2s → 0.4s → 0.8s → 1.6s
    # Handles: Database locks, concurrent access, race conditions
```

**2. Automatic Recovery on Failure**
```python
async def run_agent_with_session_recovery(max_attempts=3):
    # Detects: "Session not found" errors
    # Actions: Recreates session transparently, retries execution
```

**3. History Parsing & Reconstruction**
- Parses multiple SQLite state JSON formats
- Extracts chronological sender/message pairs
- Supports both ADK native and custom storage formats

### API Workflow
```
POST /chat → ensure_session_with_retries() → run_agent_with_session_recovery()
    ↓
Root Agent receives query → Loads conversation context from SQLite
    ↓
get_schema_tool() → rewrite_prompt_agent() → Generate SQL query
    ↓
run_sql_query_tool() → evaluate_result_agent()
    ↓
Format natural language response → Update SQLite session → Return to user
```

**Primary API Endpoints:**
- `POST /sessions/ensure` - Create or verify user session
- `GET /history/{user_id}/{session_id}` - Retrieve conversation history
- `POST /chat` - Process query and generate response
- `GET /health` - Service health check

---

## Current Limitations

### Technical Constraints

1. **Single-Instance Database Architecture**
   - No horizontal scaling capability
   - Represents single point of failure
   - Limited concurrent connection handling

2. **Static Data Snapshot**
   - No real-time HMS/EHR system integration
   - Manual data refresh required
   - No live event streaming

3. **Synchronous Request Processing**
   - No message queue implementation (Kafka/RabbitMQ)
   - Blocking API calls
   - No event-driven architecture

4. **Basic AI Configuration**
   - Generic Gemini API usage
   - No custom fine-tuning on hospital domain data
   - No vector embeddings or semantic search

5. **Performance Bottlenecks**
   - No query result caching layer
   - No database connection pooling
   - No CDN for static asset delivery

6. **Language Limitations**
   - English-only support
   - No Hindi/Marathi language processing
   - No medical terminology translation

---

## Future Development Roadmap

### Scalability Improvements
- Migrate to cloud-managed databases (AWS RDS / Google Cloud SQL / Azure Database)
- Implement Redis caching for frequently accessed queries
- Deploy database read replicas for load distribution
- Add connection pooling with PgBouncer or RDS Proxy

### Real-Time Capabilities
- WebSocket support for live data updates
- Apache Kafka implementation for event streaming
- HMS/EHR API webhook integrations
- Critical threshold alerting system

### AI Enhancement
- Vertex AI custom model fine-tuning on hospital-specific data
- Vector embeddings for semantic search capabilities
- Context-aware schema optimization
- Query result ranking using machine learning

### Enterprise Features
- Multi-language support (Hindi, Marathi, regional languages)
- Role-based access control (RBAC) implementation
- Comprehensive audit logging and compliance tracking
- Advanced analytics dashboards
- Automated report generation workflows

---

## Technology Stack

### Backend Components
- **FastAPI** - Modern Python async web framework
- **Google ADK** - Agent orchestration and management
- **LangChain** - Database utility abstractions
- **MySQL 8.0** - Primary hospital data storage
- **SQLite** - Session and conversation history
- **Uvicorn** - ASGI server with auto-reload

### Frontend Components
- **React 18** - Component-based UI library
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling

### AI/ML Infrastructure
- **Gemini 2.5 Flash** - Google's multimodal large language model
- **Google ADK Tools** - Agent framework with function calling

### DevOps & Infrastructure
- **Docker** - Application containerization
- **Docker Compose** - Multi-container orchestration
- **MySQL Connector/Python** - Database driver

---

## Project Structure
```
froncort/
├── main.py                          # FastAPI application entry point
├── Dockerfile                       # Backend container configuration
├── docker-compose.yml               # Multi-service orchestration
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (not in repo)
│
├── sql_agent/
│   ├── __init__.py
│   └── agent.py                    # Root orchestrator agent
│
├── subagents/
│   ├── __init__.py
│   ├── rewrite_prompt.py           # Query refinement agent
│   └── evaluate_result.py          # Result validation agent
│
├── functions/
│   ├── __init__.py
│   └── db_tools.py                 # Database function tools
│
├── data/
│   └── mock_pune_50_hospitals.sql  # Database initialization script
│
└── ui/                             # React frontend application
    ├── Dockerfile.frontend
    ├── package.json
    ├── index.html
    └── src/
        └── ...                     # React components
```

---

## Contributors

**Manya babbar** - Development & Implementation

---

## Acknowledgments

Built with open-source technologies:
- Google Agent Development Kit (ADK)
- LangChain Community
- FastAPI Framework
- React & Vite Ecosystem

---

**Last Updated:** November 2025
