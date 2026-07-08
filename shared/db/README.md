# Shared DB Kernel

This module contains the SQLAlchemy Base, database models, and Alembic migrations used globally across all TestLens microservices.

## Setup

```bash
pip install -r requirements.txt
```

### Local Postgres (with pgvector)

```bash
docker-compose -f docker-compose.db.yml up -d
```

### Run Migrations

To upgrade the database to the latest schema:
```bash
make migrate
```

To create a new migration after modifying models:
```bash
make migration name="add_new_table"
```

## Scaling Roadmap
Currently, `test_case_executions` holds millions of rows. Future architecture dictates partitioning `test_case_executions` by month in PostgreSQL natively (see ADR-005). We are deferring this implementation until explicit request.
