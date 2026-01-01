from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define Metrics with standard naming and labels (compatible with common dashboards)
# Adding redundant labels (service, app, application) for maximum compatibility with pre-built dashboards
REQUEST_COUNT = Counter(
    "http_requests",
    "Total number of HTTP requests",
    ["method", "handler", "status", "app_name", "service", "app", "application"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "handler", "status", "app_name", "service", "app", "application"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = time.time() - start_time

            # Labels dictionary to match definition
            metric_labels = {
                "method": method,
                "handler": endpoint,
                "status": str(status_code),
                "app_name": "fastapi",
                "service": "fastapi",
                "app": "fastapi",
                "application": "fastapi",
            }

            # Increment request counter with all defined labels
            REQUEST_COUNT.labels(**metric_labels).inc()

            # Observe request latency with all defined labels
            REQUEST_LATENCY.labels(**metric_labels).observe(process_time)

        return response


def setup_metrics(app: FastAPI):
    """Register middleware and metrics endpoint."""
    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics", include_in_schema=False)
    def metrics_endpoint():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
