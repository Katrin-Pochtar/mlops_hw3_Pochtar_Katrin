# ML Model Deployment with CI/CD

## Description

Automated deployment of Iris classification model using GitHub Actions and Render.com with Blue-Green deployment strategy.

**Model:** Logistic Regression (Iris dataset)  
**Strategy:** Blue-Green Deployment  
**Cloud:** Render.com  
**Registry:** GitHub Container Registry (ghcr.io)

## Project Structure

```
├── main.py                      # FastAPI application
├── train.py                     # Model training
├── test_model.py                # Tests
├── requirements.txt             # Dependencies
├── Dockerfile                   # Container config
├── docker-compose.blue.yml      # Blue environment (v1.0.0)
├── docker-compose.green.yml     # Green environment (v1.1.0)
├── nginx.conf                   # Load balancer
└── .github/workflows/
    └── deploy.yml               # Deployment pipeline
```

## Quick Start

### Local Setup

```bash
git clone https://github.com/Katrin-Pochtar/mlops_hw3_Pochtar_Katrin.git
cd mlops_hw3_Pochtar_Katrin
pip install -r requirements.txt
python train.py
```

### Run with Docker

```bash
docker build -t ml-service:v1.0.0 .
docker run -p 8080:8080 ml-service:v1.0.0
curl http://localhost:8080/health
```

## Blue-Green Deployment

### Local Testing

```bash
# Start Blue (v1.0.0)
docker compose -f docker-compose.blue.yml up -d
curl http://localhost:8080/health

# Start Green (v1.1.0)
docker compose -f docker-compose.green.yml up -d
curl http://localhost:8081/health
```

**Strategy:** Blue serves production while Green is validated. Traffic switches to Green after validation. Instant rollback to Blue if issues occur.

## Cloud Deployment

**Live URL:** https://ml-service-kvgp.onrender.com

### API Endpoints

**Health Check:**
```bash
curl https://ml-service-kvgp.onrender.com/health
```
Response: `{"status":"ok","version":"v1.0.0","model_loaded":true}`

**Prediction:**
```bash
curl -X POST https://ml-service-kvgp.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```
Response: `{"prediction":0,"probabilities":[0.98,0.018,0.0],"version":"v1.0.0","model_loaded":true}`

## CI/CD Pipeline

### ci.yml
- Runs tests on every push
- Trains model
- Uploads model artifact

### deploy.yml
- Builds Docker image
- Pushes to GitHub Container Registry
- Deploys to Render via webhook
- Runs health checks

### GitHub Secrets Required
- `MODEL_VERSION` - Model version (e.g., v1.0.0)
- `RENDER_DEPLOY_HOOK` - Render deployment webhook
- `RENDER_SERVICE_URL` - Service URL

## Monitoring and Logging

**Metrics:**
- Model version in all responses
- Deployment status in GitHub Actions
- Service health via /health endpoint

**Logs:**
- GitHub Actions: Repository > Actions > Workflow run
- Render: Dashboard > ml-service > Logs
- Docker: `docker logs <container_id>`

## Model Information

- **Dataset:** Iris (150 samples, 4 features, 3 classes)
- **Algorithm:** Logistic Regression
- **Accuracy:** ~96%
- **Classes:** 0=Setosa, 1=Versicolor, 2=Virginica

## Rollback

```bash
# Using Docker Compose
docker compose -f docker-compose.blue.yml up -d

# Using Render Dashboard
Dashboard > Manual Deploy > Select previous deployment > Redeploy
```
