from fastapi import FastAPI
from pydantic import BaseModel
import os
import joblib
import numpy as np

app = FastAPI(title="ML Service API", version="1.0.0")
VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

# Load model if it exists
try:
    model = joblib.load("model.pkl")
    MODEL_LOADED = True
except Exception as e:
    MODEL_LOADED = False
    model = None
    print(f"Warning: Could not load model: {e}")

# Request model for predictions
class PredictRequest(BaseModel):
    features: list[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "ML Service API",
        "version": VERSION,
        "model_loaded": MODEL_LOADED,
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": VERSION,
        "model_loaded": MODEL_LOADED
    }

@app.post("/predict")
def predict(request: PredictRequest):
    """Prediction endpoint - requires POST with features"""
    if not MODEL_LOADED:
        return {
            "error": "Model not loaded",
            "version": VERSION
        }
    
    try:
        # Make prediction
        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)
        probability = model.predict_proba(features)
        
        return {
            "prediction": int(prediction[0]),
            "probabilities": probability[0].tolist(),
            "version": VERSION,
            "model_loaded": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "version": VERSION
        }

@app.get("/predict")
def predict_get():
    """GET request handler for /predict - explains how to use POST"""
    return {
        "error": "Please use POST method",
        "message": "Send POST request with JSON body: {\"features\": [5.1, 3.5, 1.4, 0.2]}",
        "example": "curl -X POST https://ml-service-kvgp.onrender.com/predict -H 'Content-Type: application/json' -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'",
        "docs": "https://ml-service-kvgp.onrender.com/docs"
    }
