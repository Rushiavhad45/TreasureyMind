# TreasuryMind AI 🏦

**Multi-Agent Treasury & Cash Flow Optimization Platform**

A production-grade financial treasury management platform powered by a multi-agent AI system (CrewAI-style) using Google Gemini for reasoning. Built with Django + React, featuring real-time cash flow monitoring, forecasting, fund allocation, intelligent alerts, and structured approval workflows.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Port 3000)                │
│   Dashboard · Transactions · Forecasting · Fund Allocation  │
│        Alerts · Approvals · Agent Status                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API (JWT Auth)
┌──────────────────────▼──────────────────────────────────────┐
│               Django Backend (Port 8000)                    │
│  Auth · Transactions · Forecasting · Allocation · Alerts    │
│  Approvals · CashFlow · Reports · Agents                    │
└──────┬───────────────┬──────────────────┬───────────────────┘
       │               │                  │
  PostgreSQL        Redis           Multi-Agent System
  (Database)    (Broker/Cache)     ┌─────────────────┐
                       │           │  CashFlowAgent  │
               Celery Workers  ───►│  ForecastAgent  │
               (Background)    │   │  AllocationAgent│
               Celery Beat     │   │  RiskAlertAgent │
               (Scheduler)     └───│  ApprovalAgent  │
                                   └────────┬────────┘
                                            │ Gemini API
                                    Google Gemini Pro
```

---

## 🚀 Quick Start (Docker — Recommended)

### Prerequisites
- Docker 24+ and Docker Compose 2+
- Google Gemini API key (optional — falls back to statistical logic)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd treasurymind

# Configure backend environment
cp backend/.env.example backend/.env
# Edit backend/.env and set your GEMINI_API_KEY (optional)
```

### 2. Launch all services

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL, Redis
- Run Django migrations
- Seed demo data (4 users, 90 days of transactions)
- Start Celery worker + beat scheduler
- Build and serve the React frontend

### 3. Access the app

| Service        | URL                          |
|----------------|------------------------------|
| React Frontend | http://localhost:3000        |
| Django API     | http://localhost:8000/api/v1/|
| Admin Panel    | http://localhost:8000/admin/ |

---

## 🔐 Demo Login Credentials

| Role              | Email                        | Password           |
|-------------------|------------------------------|--------------------|
| Admin             | admin@treasurymind.ai        | TreasuryMind2024!  |
| Treasury Manager  | treasury@treasurymind.ai     | TreasuryMind2024!  |
| Finance Analyst   | analyst@treasurymind.ai      | TreasuryMind2024!  |
| Approver          | approver@treasurymind.ai     | TreasuryMind2024!  |

---

## 🛠️ Manual Setup (Development)

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Set up PostgreSQL database
createdb treasurymind
# (ensure DB_USER and DB_PASSWORD match .env)

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_data

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Start Celery (separate terminal)

```bash
cd backend
source venv/bin/activate

# Start worker
celery -A config.celery worker --loglevel=info

# Start scheduler (another terminal)
celery -A config.celery beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server (proxies API to localhost:8000)
npm start
```

The frontend dev server runs at http://localhost:3000 and automatically proxies `/api/` requests to the Django backend.

---

## 🤖 Multi-Agent System

The platform implements a 5-agent pipeline that runs automatically (every 6 hours via Celery Beat) or on-demand:

```
Transaction Data
      │
      ▼
┌─────────────────┐
│  CashFlowAgent  │ → Analyzes inflow/outflow, calculates liquidity score
└────────┬────────┘   Calls Gemini for insights
         │
         ▼
┌─────────────────┐
│  ForecastAgent  │ → 30-day moving average forecast
└────────┬────────┘   Stores ForecastDataPoints in DB
         │
         ▼
┌──────────────────┐
│ AllocationAgent  │ → Analyzes surplus, suggests allocations
└────────┬─────────┘   JSON breakdown: emergency/investment/payables/reserve
         │
         ▼
┌──────────────────┐
│ RiskAlertAgent   │ → Checks thresholds, creates Alert records
└────────┬─────────┘   Triggers email notifications
         │
         ▼
┌──────────────────┐
│  ApprovalAgent   │ → Creates Approval records for AI suggestions
└──────────────────┘   Logs to immutable AuditLog
```

### Triggering the Pipeline

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/trigger/ \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

**Via Frontend:** Navigate to Agent Status page → Click "Trigger Pipeline"

---

## 📡 API Reference

All endpoints require JWT authentication: `Authorization: Bearer <token>`

### Authentication
| Method | Endpoint                        | Description         |
|--------|---------------------------------|---------------------|
| POST   | `/api/v1/auth/login/`           | Login, get tokens   |
| POST   | `/api/v1/auth/logout/`          | Blacklist token     |
| POST   | `/api/v1/auth/token/refresh/`   | Refresh access token|
| GET    | `/api/v1/auth/profile/`         | Current user info   |
| GET    | `/api/v1/auth/users/`           | List users (admin)  |

### Transactions
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/transactions/`               | List (filter/search/page)|
| POST   | `/api/v1/transactions/`               | Create transaction       |
| GET    | `/api/v1/transactions/<id>/`          | Get detail               |
| PUT    | `/api/v1/transactions/<id>/`          | Update                   |
| DELETE | `/api/v1/transactions/<id>/`          | Delete                   |
| GET    | `/api/v1/transactions/summary/`       | KPIs + trends            |

### Forecasting
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/forecasts/`                  | List forecasts           |
| GET    | `/api/v1/forecasts/<id>/`             | Forecast + data points   |
| GET    | `/api/v1/forecasts/latest/`           | Most recent forecast     |
| POST   | `/api/v1/forecasts/trigger/`          | Run forecast pipeline    |

### Allocations
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/allocations/`                | List allocations         |
| GET    | `/api/v1/allocations/<id>/`           | Allocation detail        |

### Alerts
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/alerts/`                     | List alerts              |
| GET    | `/api/v1/alerts/<id>/`                | Alert detail             |
| POST   | `/api/v1/alerts/<id>/acknowledge/`    | Acknowledge alert        |
| GET    | `/api/v1/alerts/stats/`               | Alert statistics         |

### Approvals
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/approvals/`                  | List approvals           |
| GET    | `/api/v1/approvals/<id>/`             | Approval detail          |
| POST   | `/api/v1/approvals/<id>/decide/`      | Approve or reject        |
| GET    | `/api/v1/approvals/audit-logs/`       | Audit trail              |

### Agents
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/agents/logs/`                | Agent execution logs     |
| GET    | `/api/v1/agents/status/`              | Pipeline status & stats  |
| POST   | `/api/v1/agents/trigger/`             | Trigger agent pipeline   |

### CashFlow
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/v1/cashflow/metrics/`           | Rolling cashflow metrics |
| GET    | `/api/v1/cashflow/snapshots/`         | Stored snapshots         |

---

## 🗄️ Database Schema

```
users           → Custom user model (UUID PK, roles)
transactions    → Financial transactions (inflow/outflow)
cash_flows      → Daily cashflow snapshots
forecasts       → Forecast runs + data points
allocations     → AI-generated fund allocations
alerts          → System alerts + severity levels
approvals       → Approval workflow records
agent_logs      → Per-agent execution logs
audit_logs      → Immutable audit trail
reports         → Generated reports
```

---

## ⚙️ Configuration Reference

Key settings in `backend/.env`:

| Variable                  | Description                             | Default          |
|---------------------------|-----------------------------------------|------------------|
| `SECRET_KEY`              | Django secret key                       | **CHANGE THIS**  |
| `DEBUG`                   | Debug mode                              | `True`           |
| `DATABASE_URL`            | Full PostgreSQL connection URL          | localhost/5432   |
| `REDIS_URL`               | Redis connection URL                    | localhost/6379   |
| `GEMINI_API_KEY`          | Google Gemini API key                   | *(optional)*     |
| `LOW_BALANCE_THRESHOLD`   | Alert when balance < this (USD)         | `10000`          |
| `HIGH_OUTFLOW_THRESHOLD`  | Alert when daily outflow > this (USD)   | `50000`          |
| `EMAIL_BACKEND`           | Django email backend class              | console          |

---

## 📁 Project Structure

```
treasurymind/
├── docker-compose.yml
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── agents/
│   │   └── orchestrator.py       # Multi-agent pipeline
│   ├── services/
│   │   └── gemini_service.py     # Gemini API integration
│   └── apps/
│       ├── authentication/       # Users, JWT, roles
│       ├── transactions/         # Transaction CRUD
│       ├── cashflow/             # Cash flow metrics
│       ├── forecasting/          # ML forecasting
│       ├── allocation/           # Fund allocation
│       ├── alerts/               # Alert system
│       ├── approvals/            # Approval workflow
│       ├── agents/               # Agent logs & triggers
│       └── reports/              # Report generation
└── frontend/
    ├── package.json
    ├── Dockerfile
    ├── nginx.conf
    └── src/
        ├── App.jsx
        ├── index.js
        ├── index.css             # Dark financial theme
        ├── store/
        │   └── authStore.js      # Zustand auth state
        ├── services/
        │   └── api.js            # Axios + JWT interceptors
        ├── components/
        │   └── common/
        │       └── Layout.jsx    # Sidebar + topbar
        └── pages/
            ├── Login.jsx
            ├── Dashboard.jsx
            ├── Transactions.jsx
            ├── Forecasting.jsx
            ├── FundAllocation.jsx
            ├── Alerts.jsx
            ├── Approvals.jsx
            └── AgentStatus.jsx
```

---

## 🧪 Development Tips

### Run only specific Celery tasks manually

```python
# In Django shell: python manage.py shell
from apps.agents.tasks import run_full_agent_pipeline
result = run_full_agent_pipeline.delay()
print(result.get(timeout=60))
```

### Check Celery task status

```bash
# Flower (Celery monitoring UI)
pip install flower
celery -A config.celery flower --port=5555
# Open http://localhost:5555
```

### Reset and re-seed data

```bash
python manage.py flush --noinput
python manage.py seed_data
```

---

## 🔒 Security Notes

- Change `SECRET_KEY` before deploying to production
- Set `DEBUG=False` in production
- Use environment variables for all secrets — never commit `.env`
- JWT tokens expire in 60 minutes (configurable)
- All financial amounts use `DecimalField` (no floating-point errors)
- AuditLog records are append-only (no update/delete permissions)

---

## 📄 License

MIT License — Built for educational and demonstration purposes.
