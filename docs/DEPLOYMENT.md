# Deployment Guide - Presidio-NL v2

## Overzicht

Deze guide beschrijft hoe Presidio-NL v2 is gedeployed op Kubernetes met ArgoCD voor GitOps.

## Architectuur

### Kubernetes Resources
- **Namespace**: `presidio-nl-v2`
- **Deployment**: 1-5 replicas met auto-scaling
- **Service**: ClusterIP op poort 8080
- **Ingress**: NGINX met Let's Encrypt SSL
- **PVC**: 25Gi NFS storage voor persistente data
- **HPA**: Auto-scaling op basis van CPU (80% threshold)
- **NetworkPolicy**: Security policies voor network access
- **ServiceAccount**: Dedicated service account met security context

### Container Specificaties
- **Image**: `ghcr.io/mwest2020/presidio-nl-v2:latest`
- **Port**: 8080 (intern)
- **Resources**: 
  - Requests: 4Gi memory, 500m CPU
  - Limits: 8Gi memory, 1500m CPU
- **Security**: 
  - Non-root user (UID 1000)
  - Read-only root filesystem
  - Dropped capabilities

### Volumes
- **Storage Volume**: `/app/storage` (PersistentVolume, 25Gi NFS)
- **Models Cache**: `/app/models` (EmptyDir voor HuggingFace cache)

### Environment Variables
```yaml
- API_HOST: "0.0.0.0"
- API_PORT: "8080"
- DEBUG: "false"
- LOG_LEVEL: "info"
- TRANSFORMERS_CACHE: "/app/models"
- HF_HOME: "/app/models"
- TORCH_HOME: "/app/models"
- STORAGE_DIR: "/app/storage"
- MAX_STORAGE_TIME: "3600"
```

## Deployment Process

### 1. Voorbereiding
Zorg dat je toegang hebt tot het juiste Kubernetes cluster:
```bash
export KUBECONFIG=/path/to/your/kubeconfig.yaml
```

### 2. Manifests Toepassen
```bash
# Alle manifests in één keer
kubectl apply -f k8s/

# Of stap voor stap
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/networkpolicy.yaml
```

### 3. Verificatie
```bash
# Check alle resources
kubectl get all,pvc,hpa,networkpolicy -n presidio-nl-v2

# Check pod status
kubectl get pods -n presidio-nl-v2

# Check logs
kubectl logs -f deployment/presidio-nl-v2 -n presidio-nl-v2

# Check ingress en certificaat
kubectl get ingress,certificates -n presidio-nl-v2
```

## ArgoCD Integration

### GitOps Workflow
1. **Code Changes**: Push naar `main` branch
2. **ArgoCD Sync**: Automatische detectie van wijzigingen in `k8s/` directory
3. **Deployment**: ArgoCD past wijzigingen toe op target cluster

### ArgoCD Application
De ArgoCD application is geconfigureerd voor cross-cluster deployment:
- **Source**: GitHub repository `k8s/` directory
- **Target**: Target cluster
- **Sync Policy**: Automatisch

## Monitoring & Troubleshooting

### Health Checks
- **Liveness Probe**: `GET /health` (60s initial delay, 30s interval)
- **Readiness Probe**: `GET /health` (30s initial delay, 10s interval)

### Common Issues

#### Pod Start Problemen
```bash
# Check pod events
kubectl describe pod <pod-name> -n presidio-nl-v2

# Check resource constraints
kubectl top pods -n presidio-nl-v2
```

#### Storage Issues
```bash
# Check PVC status
kubectl get pvc -n presidio-nl-v2

# Check storage class
kubectl get storageclass
```

#### SSL Certificate Issues
```bash
# Check certificate status
kubectl get certificates -n presidio-nl-v2

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

### Scaling
```bash
# Manual scaling
kubectl scale deployment presidio-nl-v2 --replicas=3 -n presidio-nl-v2

# Check HPA status
kubectl get hpa -n presidio-nl-v2
```

## Security

### Network Policies
- Ingress: Alleen toegang vanuit ingress-nginx namespace
- Egress: Alle uitgaande verbindingen toegestaan

### Security Context
- Non-root user (UID 1000)
- Read-only root filesystem
- Dropped alle capabilities
- No privilege escalation

### Secrets Management
- SSL certificates beheerd door cert-manager
- Geen hardcoded secrets in manifests

## Backup & Recovery

### Data Backup
De persistente data in `/app/storage` wordt automatisch gebackupt via de NFS storage backend.

### Disaster Recovery
1. **Namespace Recreation**: `kubectl apply -f k8s/namespace.yaml`
2. **Full Restore**: `kubectl apply -f k8s/`
3. **Data Verification**: Check dat PVC correct gemount is

## Performance Tuning

### Resource Optimization
- **Memory**: 4-8Gi voor ML model loading
- **CPU**: 500m-1500m voor text processing
- **Storage**: NFS voor betere I/O performance

### Scaling Parameters
- **Min Replicas**: 1 (cost optimization)
- **Max Replicas**: 5 (load handling)
- **CPU Threshold**: 80% (responsive scaling)

## Maintenance

### Updates
1. **Image Update**: Push nieuwe image naar registry
2. **Manifest Update**: Update image tag in `k8s/deployment.yaml`
3. **Git Commit**: ArgoCD detecteert en deployt automatisch

### Rollback
```bash
# Check deployment history
kubectl rollout history deployment/presidio-nl-v2 -n presidio-nl-v2

# Rollback naar vorige versie
kubectl rollout undo deployment/presidio-nl-v2 -n presidio-nl-v2
``` 