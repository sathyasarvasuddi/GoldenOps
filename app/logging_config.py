import json
import logging
import os
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service_name": os.getenv("SERVICE_NAME", "goldenops"),
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "message": record.getMessage(),
        }

        fields = (
            "event_name",
            "request_id",
            "method",
            "path",
            "status",
            "latency_ms",
            "error_type",
        )

        for field in fields:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(payload, default=str)


def configure_logging():
    formatter = JsonFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("/app/logs/goldenops.log")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    root.setLevel(logging.INFO)
