import logging
import random
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("goldenops")

app = FastAPI(title="GoldenOps", version="0.1.0")

REQUEST_COUNT = Counter(
    "goldenops_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "goldenops_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    status = 500

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        duration = time.perf_counter() - start
        path = request.url.path

        REQUEST_COUNT.labels(
            request.method, path, str(status)
        ).inc()

        REQUEST_LATENCY.labels(
            request.method, path
        ).observe(duration)

        logger.info(
            "http_request",
            extra={
                "event_name": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "status": status,
                "latency_ms": round(duration * 1000, 2),
            },
        )


@app.get("/health")
def health():
    return {"status": "UP", "service": "goldenops"}


@app.get("/api/users")
def users():
    logger.info(
        "users_request",
        extra={
            "event_name": "users_request",
            "service": "goldenops",
        },
    )
    return {"users": [{"id": 1, "name": "demo-user"}]}


@app.get("/api/orders")
def orders():
    logger.info(
        "orders_request",
        extra={
            "event_name": "orders_request",
            "service": "goldenops",
        },
    )
    return {"orders": [{"id": "ORD-1001", "status": "COMPLETED"}]}


@app.post("/api/payments")
def payments(
    request: Request,
    simulate: Optional[str] = None,
):
    request_id = request.state.request_id

    if simulate == "slow":
        time.sleep(3)

    elif simulate == "timeout":
        logger.error(
            "payment_timeout",
            extra={
                "event_name": "payment_timeout",
                "service": "goldenops",
                "request_id": request_id,
                "error_type": "DatabaseTimeout",
            },
        )
        raise HTTPException(
            status_code=504,
            detail="Database timeout",
        )

    elif simulate == "error":
        logger.error(
            "payment_failure",
            extra={
                "event_name": "payment_failure",
                "service": "goldenops",
                "request_id": request_id,
                "error_type": "PaymentProcessingError",
            },
        )
        raise HTTPException(
            status_code=500,
            detail="Payment processing failed",
        )

    logger.info(
        "payment_success",
        extra={
            "event_name": "payment_success",
            "service": "goldenops",
            "request_id": request_id,
        },
    )

    return {
        "status": "SUCCESS",
        "request_id": request_id,
    }


@app.get("/api/random-failure")
def random_failure():
    if random.random() < 0.3:
        logger.error(
            "random_failure",
            extra={
                "event_name": "random_failure",
                "service": "goldenops",
                "error_type": "DependencyUnavailable",
            },
        )
        raise HTTPException(
            status_code=503,
            detail="Dependency unavailable",
        )

    return {"status": "SUCCESS"}


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "unhandled_exception",
        extra={
            "event_name": "unhandled_exception",
            "service": "goldenops",
            "path": request.url.path,
            "error_type": type(exc).__name__,
        },
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
