import json
import random
import time
import uuid
import os
from datetime import datetime, timezone


SERVICES = [
    "orders-api",
    "payment-api",
    "inventory-api",
    "auth-api",
    "product-api",
]

ENDPOINTS = [
    ("GET", "/api/orders"),
    ("POST", "/api/orders"),
    ("GET", "/api/products"),
    ("GET", "/api/inventory"),
    ("POST", "/api/payments"),
    ("POST", "/api/login"),
]

STATUS_CODES = [
    200, 200, 200, 200,
    201,
    400,
    401,
    404,
    500,
    502,
]

ERRORS = [
    "PaymentGatewayTimeout",
    "DatabaseConnectionError",
    "AuthenticationFailed",
    "InventoryUnavailable",
    "InternalServerError",
]


def generate_log():
    method, path = random.choice(ENDPOINTS)
    status = random.choice(STATUS_CODES)

    level = "INFO"

    if status >= 500:
        level = "ERROR"
    elif status >= 400:
        level = "WARN"

    log = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "service_name": random.choice(SERVICES),
        "environment": "dev",
        "level": level,
        "event_name": "http_request",
        "method": method,
        "path": path,
        "status": status,
        "latency_ms": round(random.uniform(5, 2500), 2),
        "request_id": str(uuid.uuid4()),
        "user_id": f"user-{random.randint(1000, 9999)}",
        "source_ip": f"10.0.{random.randint(1, 10)}.{random.randint(1, 254)}",
    }

    if status >= 400:
        log["error_type"] = random.choice(ERRORS)

    return log


LOG_FILE = "/logs/goldenops-api.log"

os.makedirs("/logs", exist_ok=True)

while True:
    log = generate_log()
    log_line = json.dumps(log)

    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

    print(log_line, flush=True)

    time.sleep(random.uniform(0.5, 3))