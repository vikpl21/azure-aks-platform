import os
import time
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from model import predict

logger = logging.getLogger(__name__)

APPINSIGHTS_CONNECTION_STRING = os.getenv("APPINSIGHTS_CONNECTION_STRING", "")

if APPINSIGHTS_CONNECTION_STRING:
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor(connection_string=APPINSIGHTS_CONNECTION_STRING)
    print(">>> Azure Monitor OpenTelemetry configured", flush=True)
    logger.info("Azure Monitor OpenTelemetry configured")

app = FastAPI(title="ML Inference API", version="1.0.0")

if APPINSIGHTS_CONNECTION_STRING:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)
    print(">>> FastAPI instrumented with OpenTelemetry", flush=True)
    logger.info("FastAPI instrumented with OpenTelemetry")

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["endpoint"]
)


class PredictRequest(BaseModel):
    features: list[float]


class PredictResponse(BaseModel):
    class_id: int
    class_name: str
    probability: float


@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    start = time.time()
    if len(request.features) != 4:
        REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="400").inc()
        raise HTTPException(status_code=400, detail="Expected 4 features")
    try:
        result = predict(request.features)
        REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
        REQUEST_LATENCY.labels(endpoint="/predict").observe(time.time() - start)
        logger.info(f"Prediction: class={result['class_name']} prob={result['probability']}")
        return result
    except Exception as e:
        REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
