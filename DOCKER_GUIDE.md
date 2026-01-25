# Docker Deployment Guide

## Structure
```
MLOps/
├── backend/src/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── api.py
│   └── preprocessing_fraud_class.py
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── front.py
├── notebooks/
│   ├── processors/
│   └── model_registry/
└── docker-compose.yml
```

## Build Commands

### Build all services
```bash
docker-compose build
```

### Build specific service
```bash
docker-compose build backend
docker-compose build frontend
```

## Run Commands

### Start all services
```bash
docker-compose up
```

### Start in detached mode (background)
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes
```bash
docker-compose down -v
```

## Access

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:8501

## Troubleshooting

### Rebuild without cache
```bash
docker-compose build --no-cache
```

### Remove all containers and images
```bash
docker-compose down --rmi all
```

### Check service health
```bash
docker-compose ps
```
