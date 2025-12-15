from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
import joblib
import numpy as np
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service API", version="1.0.0")
VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

# Metrics storage
metrics = {
    "total_predictions": 0,
    "successful_predictions": 0,
    "failed_predictions": 0,
    "total_latency": 0.0,
    "start_time": datetime.now().isoformat()
}

# Load model if it exists
try:
    model = joblib.load("model.pkl")
    MODEL_LOADED = True
    logger.info(f" Model loaded successfully - Version: {VERSION}")
except Exception as e:
    MODEL_LOADED = False
    model = None
    logger.error(f"Could not load model: {e}")

# Request model for predictions
class PredictRequest(BaseModel):
    features: list[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host}")
    
    response = await call_next(request)
    
    # Calculate latency
    latency = time.time() - start_time
    
    # Log response
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Latency: {latency:.3f}s")
    
    return response

@app.get("/")
def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "ML Service API",
        "version": VERSION,
        "model_loaded": MODEL_LOADED,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "predict": "/predict (POST)",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint with detailed status"""
    logger.info(f"Health check - Version: {VERSION}, Model loaded: {MODEL_LOADED}")
    
    return {
        "status": "ok" if MODEL_LOADED else "degraded",
        "version": VERSION,
        "model_loaded": MODEL_LOADED,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
def get_metrics():
    """Endpoint to view service metrics"""
    logger.info("Metrics endpoint accessed")
    
    avg_latency = (
        metrics["total_latency"] / metrics["total_predictions"] 
        if metrics["total_predictions"] > 0 
        else 0
    )
    
    success_rate = (
        (metrics["successful_predictions"] / metrics["total_predictions"] * 100)
        if metrics["total_predictions"] > 0
        else 0
    )
    
    return {
        "version": VERSION,
        "model_loaded": MODEL_LOADED,
        "total_predictions": metrics["total_predictions"],
        "successful_predictions": metrics["successful_predictions"],
        "failed_predictions": metrics["failed_predictions"],
        "success_rate_percent": round(success_rate, 2),
        "average_latency_seconds": round(avg_latency, 3),
        "uptime_since": metrics["start_time"]
    }

@app.post("/predict")
def predict(request: PredictRequest):
    """Prediction endpoint - requires POST with features"""
    start_time = time.time()
    metrics["total_predictions"] += 1
    
    logger.info(f"Prediction request received - Features: {request.features}")
    
    if not MODEL_LOADED:
        metrics["failed_predictions"] += 1
        logger.error("Prediction failed - Model not loaded")
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Make prediction
        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)
        probability = model.predict_proba(features)
        
        # Calculate latency
        latency = time.time() - start_time
        metrics["total_latency"] += latency
        metrics["successful_predictions"] += 1
        
        logger.info(
            f"Prediction successful - Class: {prediction[0]}, "
            f"Confidence: {max(probability[0]):.2%}, Latency: {latency:.3f}s"
        )
        
        return {
            "prediction": int(prediction[0]),
            "probabilities": probability[0].tolist(),
            "confidence": float(max(probability[0])),
            "version": VERSION,
            "model_loaded": True,
            "latency_seconds": round(latency, 3)
        }
    except Exception as e:
        metrics["failed_predictions"] += 1
        logger.error(f" Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict")
def predict_get():
    """GET request handler for /predict - explains how to use POST"""
    logger.info("GET request to /predict - redirecting to docs")
    return {
        "error": "Please use POST method",
        "message": "Send POST request with JSON body: {\"features\": [5.1, 3.5, 1.4, 0.2]}",
        "example": "curl -X POST https://ml-service-kvgp.onrender.com/predict -H 'Content-Type: application/json' -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'",
        "docs": "https://ml-service-kvgp.onrender.com/docs"
    }