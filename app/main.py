from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
from model import predict

app = FastAPI(title="ML Inference API", version="1.0.0")

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
        return result
    except Exception as e:
        REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
