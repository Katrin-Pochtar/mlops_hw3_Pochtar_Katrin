# ML Model Deployment

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

**Notifications:**

- GitHub Actions sends automatic notifications via GitHub UI
- Deployment status visible in Actions tab
- Optional: Configure email notifications via workflow (requires SMTP credentials)

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


## Screenshots after succesfull deploy

## Deployment Strategy Verification
<img width="727" height="64" alt="Screenshot 2025-12-14 at 21 09 27" src="https://github.com/user-attachments/assets/4c0f483a-12c1-4de1-94c6-47273fd87859" />

## GitHub Actions green check
<img width="1426" height="403" alt="Screenshot 2025-12-15 at 22 22 09" src="https://github.com/user-attachments/assets/7f031b59-ae7a-43b8-a868-05655f47bdb6" />

## Cloud Deployment & Logs
<img width="1214" height="724" alt="Screenshot 2025-12-15 at 22 21 00" src="https://github.com/user-attachments/assets/7083e77e-77d0-4650-b90e-99d6ad5820a7" />

## API Endpoints Check
<img width="767" height="133" alt="Screenshot 2025-12-14 at 23 11 11" src="https://github.com/user-attachments/assets/b807afc1-371e-4447-a1fa-b86f2e5b8b44" />

## Notifications
<img width="505" height="252" alt="Screenshot 2025-12-15 at 22 23 42" src="https://github.com/user-attachments/assets/6affb8f5-c086-4e7c-b8ee-dc679b23161b" />






