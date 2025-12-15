from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import joblib

app = FastAPI()
VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

model = None
try:
    if os.path.exists("model.pkl"):
        model = joblib.load("model.pkl")
    else:
        print("WARNING: model.pkl not found. Predictions will fail.")
except Exception as e:
    print(f"Error loading model: {e}")

class InputData(BaseModel):
    x: list[float]

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "version": VERSION, 
        "model_loaded": model is not None
    }

@app.get("/predict")
def predict(data: InputData):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        prediction = model.predict([data.x])
        
        return {
            "prediction": int(prediction[0]), 
            "version": VERSION
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Input error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))