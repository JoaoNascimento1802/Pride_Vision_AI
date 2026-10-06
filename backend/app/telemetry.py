# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import logging
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram
from pythonjsonlogger import jsonlogger

# Context variable for request ID
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

# Prometheus Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route"]
)

# Business Metrics
normalizer_duration_seconds = Histogram(
    "normalizer_duration_seconds",
    "Duration of finding normalization in seconds",
    ["tool"]
)

background_tasks_queue_size = Gauge(
    "background_tasks_queue_size",
    "Current number of pending background tasks"
)

external_calls_errors_total = Counter(
    "external_calls_errors_total",
    "Total errors when calling external services",
    ["service", "error_type"]
)

db_active_connections = Gauge(
    "db_active_connections",
    "Number of active database connections (estimated)"
)

class RequestIdFilter(logging.Filter):
    """Adiciona o request_id ao registro de log."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True

def setup_telemetry() -> None:
    """Configura o logging em JSON."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler()

    formatter = jsonlogger.JsonFormatter(  # type: ignore
        "%(asctime)s %(levelname)s %(name)s %(module)s %(message)s %(request_id)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"}
    )
    handler.setFormatter(formatter)

    handler.addFilter(RequestIdFilter())
    logger.addHandler(handler)

    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.handlers.clear()

async def telemetry_middleware(request: Request, call_next: Callable[[Request], Any]) -> Response:
    """Middleware para capturar métricas e correlation ID."""
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx.set(req_id)

    start_time = time.perf_counter()

    route = request.url.path
    if request.scope.get("route"):
        route = request.scope["route"].path

    try:
        response: Response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        logging.getLogger("telemetry").exception("Internal Server Error", extra={"error": str(e)})
        raise e
    finally:
        duration = time.perf_counter() - start_time

        if route != "/metrics":
            http_requests_total.labels(
                method=request.method,
                route=route,
                status_code=str(status_code)
            ).inc()

            http_request_duration_seconds.labels(
                method=request.method,
                route=route
            ).observe(duration)

        request_id_ctx.reset(token)

    return response
