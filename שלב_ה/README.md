# Stage 5 — Graphical User Interface

Python 3 desktop application for the Medical Laboratory Management System. Connects to the existing PostgreSQL database (Docker) with full CRUD, analytics, and Stage 4 PL/pgSQL integration.

## Architecture

```
שלב_ה/
├── main.py                 # Application entry point & navigation
├── config.py               # .env / environment configuration
├── db_manager.py           # Connection pool, queries, error mapping
├── requirements.txt
├── .env.example
├── utils/
│   ├── theme.py            # Typography & spacing
│   └── dialogs.py          # Success / error / confirm dialogs
└── views/
    ├── dashboard.py        # Home / sidebar navigation
    ├── connection_error.py # Startup DB failure screen
    ├── crud/
    │   ├── table_configs.py  # Per-table SQL & field metadata
    │   └── generic_crud.py   # Reusable CRUD with smart lookup
    └── analytics/
        └── analytics_screen.py  # Stage 2 queries + Stage 4 callers
```

| Layer | Responsibility |
|-------|----------------|
| `config` | Loads `DB_HOST`, credentials, schema, theme from `.env` |
| `db_manager` | `ThreadedConnectionPool`, transactions, trigger-friendly errors |
| `table_configs` | JOIN-based list queries, FK dropdown SQL, CRUD statements |
| `generic_crud` | Smart PK lookup, form population, Treeview grid |
| `analytics_screen` | Stage 2 queries, procedures, `fn_get_doctor_workload` |

## Quick start

```bash
cd שלב_ה
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env to match your docker-compose secrets
python main.py
```

### Docker connection

| Where the GUI runs | `DB_HOST` value |
|--------------------|-----------------|
| On your host (native Python) | `localhost` |
| Inside Docker Compose network | `db` (service name from `docker-compose.yml`) |

Ensure the database container is up:

```bash
docker compose up -d db
```

Deploy Stage 3 (`staff_remote`) and Stage 4 objects before using analytics features.

## Features

- **Dashboard** — Sidebar navigation to all CRUD modules and analytics
- **CRUD** — All six lab tables with human-readable FK labels (no raw IDs in grids/dropdowns)
- **Smart update** — Enter PK → Load → edit → Save
- **Analytics** — `select_2` popular tests, `select_6` urgent monitoring
- **Procedures** — `pr_update_all_order_prices`, `pr_promote_technicians` (NOTICE log dialog)
- **Function** — `fn_get_doctor_workload` with doctor picker from `staff_remote`
- **Trigger errors** — `trg_status_protection` and similar messages shown in friendly dialogs
- **Dark / light mode** — Toggle from the dashboard sidebar
