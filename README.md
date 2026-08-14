# GoldenOps

Zero-cost-first observability engineering project.

## Current phase

Phase 1:
- FastAPI application
- Structured JSON logging
- Request IDs
- Prometheus metrics
- Failure simulation
- Automated tests

Docker is intentionally excluded from this version. We will build Docker manually as part of the learning phase.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

## Endpoints

- GET `/health`
- GET `/api/users`
- GET `/api/orders`
- POST `/api/payments`
- GET `/api/random-failure`
- GET `/metrics`
- GET `/docs`

## Test scenarios

```bash
curl http://localhost:8000/health

curl http://localhost:8000/api/users

curl http://localhost:8000/api/orders

curl -X POST "http://localhost:8000/api/payments?simulate=slow"

curl -X POST "http://localhost:8000/api/payments?simulate=error"

curl -X POST "http://localhost:8000/api/payments?simulate=timeout"

curl http://localhost:8000/api/random-failure

curl http://localhost:8000/metrics
```

## Planned phases

1. Application
2. Docker — built manually for learning
3. Filebeat
4. Logstash + Grok
5. Elasticsearch + Kibana
6. ILM and alerting
7. OpenSearch
8. ELK → OpenSearch migration
9. Snapshot/restore to S3
10. GitHub Actions CI/CD
11. AWS deployment
12. Kubernetes observability
