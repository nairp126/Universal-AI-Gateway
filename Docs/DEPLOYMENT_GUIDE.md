# 🚢 Deployment Guide

Guidelines for deploying the Universal LLM Gateway to production environments.

## 📦 Containerization

The project includes a production-grade, multi-stage `Dockerfile`.

### Build Image

```bash
docker build -t llm-gateway:latest .
```

### Resource Recommendations

- **CPU**: 1-2 vCPU per instance.
- **Memory**: 2GB RAM minimum (4GB recommended for heavy semantic caching).

---

## ☸️ Kubernetes Deployment

We provide standard manifests in the `k8s/` directory.

### Deploy to Cluster

```bash
kubectl apply -f k8s/
```

### Core Components

- **Deployment**: Horizontally scalable gateway pods.
- **Service**: Internal load balancing.
- **ConfigMap**: Non-sensitive environment variables.
- **Secrets**: API keys and database credentials.

---

## 🛡️ Production Hardening

Checklist for production readiness:

1. [ ] **SSL/TLS**: Ensure ALB/Ingress terminates SSL.
2. [ ] **Database**: Use a managed Postgres service (e.g., AWS RDS) with backups enabled.
3. [ ] **Redis**: Use a managed Redis service (e.g., AWS ElastiCache) for HA.
4. [ ] **Security**: Change the default `ADMIN_API_KEY` immediately.
5. [ ] **Observability**: Import `grafana-dashboard.json` into your monitoring stack.

---

## 🔄 Horizontal Scaling

The gateway is stateless. Scale the `Deployment` replicas based on CPU/Memory utilization or request counts.

```bash
kubectl autoscale deployment gateway --cpu-percent=70 --min=2 --max=10
```
