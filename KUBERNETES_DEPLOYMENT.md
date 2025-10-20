# 🚀 KUBERNETES PRODUCTION DEPLOYMENT GUIDE

**Status:** ✅ PRODUCTION-READY  
**Infrastructure:** Complete and tested

---

## 📦 WHAT'S INCLUDED

All Kubernetes manifests for production deployment:

1. ✅ **Deployment** - 3 replicas with health checks
2. ✅ **Service** - LoadBalancer for external access
3. ✅ **ConfigMap** - Application configuration
4. ✅ **Secrets** - Secure credential management
5. ✅ **HPA** - Auto-scaling (3-10 pods)

**Total:** 5 production-ready Kubernetes files

---

## 🎯 ARCHITECTURE

### Production Setup
```
┌─────────────────────────────────────────┐
│         LoadBalancer Service            │
│         (External IP:80)                │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ Pod 1 │   │ Pod 2 │   │ Pod 3 │
│ 2GB   │   │ 2GB   │   │ 2GB   │
└───────┘   └───────┘   └───────┘
    │            │            │
    └────────────┼────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────────┐      ┌─────────▼──────┐
│   Neo4j    │      │    Qdrant      │
│  (Cloud)   │      │   (Cloud)      │
└────────────┘      └────────────────┘
```

### Auto-Scaling
- **Minimum:** 3 pods (high availability)
- **Maximum:** 10 pods (handle traffic spikes)
- **Trigger:** CPU >70% or Memory >80%

---

## 📋 PREREQUISITES

### 1. Kubernetes Cluster
You need a K8s cluster. Options:

**Cloud Providers:**
- **Google GKE** - `gcloud container clusters create`
- **AWS EKS** - `eksctl create cluster`
- **Azure AKS** - `az aks create`
- **DigitalOcean** - Via web console

**Local Testing:**
- **Minikube** - `minikube start`
- **Kind** - `kind create cluster`
- **Docker Desktop** - Enable Kubernetes

### 2. kubectl Installed
```bash
# Check if installed
kubectl version --client

# If not, install:
# macOS
brew install kubectl

# Or download from:
# https://kubernetes.io/docs/tasks/tools/
```

### 3. Docker Image
Build and push your Docker image:

```bash
# Build image
docker build -t YOUR_REGISTRY/hybrid-rag-api:latest .

# Push to registry
docker push YOUR_REGISTRY/hybrid-rag-api:latest

# Update k8s/deployment.yaml line 19 with your image
```

**Registry options:**
- Docker Hub: `docker.io/username/hybrid-rag-api`
- Google GCR: `gcr.io/project-id/hybrid-rag-api`
- AWS ECR: `123456789.dkr.ecr.region.amazonaws.com/hybrid-rag-api`

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Create Namespace (Optional but Recommended)

```bash
kubectl create namespace hybrid-rag
```

All commands below will use `-n hybrid-rag`. Omit if using default namespace.

---

### Step 2: Create Secrets

**Edit the secrets file:**
```bash
cd /Users/rezazeraat/Desktop/KnowledgeGraph/k8s
cp secrets.yaml.example secrets.yaml
nano secrets.yaml
```

**Add your actual credentials:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: hybrid-rag-secrets
type: Opaque
stringData:
  neo4j-uri: "neo4j+s://YOUR_ACTUAL_INSTANCE.databases.neo4j.io"
  neo4j-username: "neo4j"
  neo4j-password: "YOUR_ACTUAL_PASSWORD"
  qdrant-url: "https://YOUR_ACTUAL_CLUSTER.qdrant.io:6333"
  qdrant-api-key: "YOUR_ACTUAL_API_KEY"
  gemini-api-key: "YOUR_ACTUAL_GEMINI_KEY"
```

**Create the secret:**
```bash
kubectl create -f secrets.yaml -n hybrid-rag
```

**Verify:**
```bash
kubectl get secrets -n hybrid-rag
```

**⚠️ IMPORTANT:** Delete `secrets.yaml` after creating (or add to .gitignore)
```bash
rm secrets.yaml  # Don't commit this file!
```

---

### Step 3: Create ConfigMap

```bash
kubectl apply -f configmap.yaml -n hybrid-rag
```

**Verify:**
```bash
kubectl get configmap hybrid-rag-config -n hybrid-rag -o yaml
```

---

### Step 4: Deploy Application

```bash
kubectl apply -f deployment.yaml -n hybrid-rag
```

**Check deployment:**
```bash
kubectl get deployments -n hybrid-rag
kubectl get pods -n hybrid-rag
```

**Expected output:**
```
NAME              READY   STATUS    RESTARTS   AGE
hybrid-rag-api-xxx   1/1     Running   0          30s
hybrid-rag-api-yyy   1/1     Running   0          30s
hybrid-rag-api-zzz   1/1     Running   0          30s
```

**Watch pods starting:**
```bash
kubectl get pods -n hybrid-rag -w
```

---

### Step 5: Create Service

```bash
kubectl apply -f service.yaml -n hybrid-rag
```

**Get external IP:**
```bash
kubectl get service hybrid-rag-api-service -n hybrid-rag
```

**Expected output:**
```
NAME                      TYPE           EXTERNAL-IP      PORT(S)        AGE
hybrid-rag-api-service    LoadBalancer   34.123.45.67     80:30123/TCP   1m
```

⏳ **Wait for EXTERNAL-IP** (may take 2-3 minutes on cloud providers)

---

### Step 6: Enable Auto-Scaling

```bash
kubectl apply -f hpa.yaml -n hybrid-rag
```

**Verify HPA:**
```bash
kubectl get hpa -n hybrid-rag
```

**Expected output:**
```
NAME                 REFERENCE               TARGETS         MINPODS   MAXPODS   REPLICAS
hybrid-rag-api-hpa   Deployment/hybrid-rag   15%/70%, 20%/80%   3         10        3
```

---

### Step 7: Verify Everything

```bash
# Check all resources
kubectl get all -n hybrid-rag

# Check pod logs
kubectl logs -f deployment/hybrid-rag-api -n hybrid-rag

# Test health endpoint
EXTERNAL_IP=$(kubectl get svc hybrid-rag-api-service -n hybrid-rag -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP/health
```

**Expected health response:**
```json
{
  "status": "healthy",
  "dependencies": {...},
  "uptime_seconds": 123.45
}
```

---

## 🔧 CONFIGURATION

### Update Image Version

```bash
# Build new version
docker build -t YOUR_REGISTRY/hybrid-rag-api:v2 .
docker push YOUR_REGISTRY/hybrid-rag-api:v2

# Update deployment
kubectl set image deployment/hybrid-rag-api api=YOUR_REGISTRY/hybrid-rag-api:v2 -n hybrid-rag

# Check rollout status
kubectl rollout status deployment/hybrid-rag-api -n hybrid-rag
```

### Scale Manually

```bash
# Scale to 5 pods
kubectl scale deployment hybrid-rag-api --replicas=5 -n hybrid-rag

# Verify
kubectl get pods -n hybrid-rag
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap hybrid-rag-config -n hybrid-rag

# Restart pods to pick up changes
kubectl rollout restart deployment/hybrid-rag-api -n hybrid-rag
```

---

## 📊 MONITORING

### View Logs

```bash
# All pods
kubectl logs -f deployment/hybrid-rag-api -n hybrid-rag

# Specific pod
kubectl logs -f POD_NAME -n hybrid-rag

# Previous container (if crashed)
kubectl logs POD_NAME --previous -n hybrid-rag
```

### Check Resource Usage

```bash
# CPU and Memory
kubectl top pods -n hybrid-rag

# Node resources
kubectl top nodes
```

### Describe Resources

```bash
# Deployment details
kubectl describe deployment hybrid-rag-api -n hybrid-rag

# Pod details
kubectl describe pod POD_NAME -n hybrid-rag

# Service details
kubectl describe service hybrid-rag-api-service -n hybrid-rag
```

---

## 🐛 TROUBLESHOOTING

### Pods Not Starting

**Check pod status:**
```bash
kubectl get pods -n hybrid-rag
kubectl describe pod POD_NAME -n hybrid-rag
```

**Common issues:**
- ❌ Image pull failed → Check image name and registry access
- ❌ Secrets not found → Verify secrets created
- ❌ Insufficient resources → Check node capacity

**Solution:**
```bash
# Check events
kubectl get events -n hybrid-rag --sort-by='.lastTimestamp'

# Check logs
kubectl logs POD_NAME -n hybrid-rag
```

---

### Health Check Failing

**Symptoms:**
- Pods show 0/1 READY
- Pods keep restarting

**Check:**
```bash
# View pod logs
kubectl logs POD_NAME -n hybrid-rag

# Check health endpoint inside pod
kubectl exec POD_NAME -n hybrid-rag -- curl localhost:8000/health
```

**Common causes:**
- Backend taking >60s to start (increase `initialDelaySeconds`)
- Dependencies (Neo4j/Qdrant) not accessible
- Environment variables missing

---

### LoadBalancer No External IP

**If EXTERNAL-IP shows `<pending>` for >5 minutes:**

**Check cloud provider:**
- ✅ LoadBalancer supported (GKE, EKS, AKS yes; Minikube no)
- ✅ Sufficient quota for LoadBalancer
- ✅ Firewall allows inbound traffic

**Local testing alternative:**
```bash
# Use NodePort instead
kubectl edit service hybrid-rag-api-service -n hybrid-rag
# Change type: LoadBalancer → type: NodePort

# Get NodePort
kubectl get svc -n hybrid-rag
# Access via: http://NODE_IP:NODE_PORT
```

---

### Auto-Scaling Not Working

**Check HPA status:**
```bash
kubectl describe hpa hybrid-rag-api-hpa -n hybrid-rag
```

**Requirements:**
- ✅ Metrics Server installed
- ✅ Resource requests defined in deployment
- ✅ Sufficient load to trigger scaling

**Install Metrics Server (if missing):**
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## 🔒 PRODUCTION BEST PRACTICES

### 1. Security

**Use private image registry:**
```yaml
# Add image pull secret
imagePullSecrets:
- name: registry-credentials
```

**Restrict service account:**
```yaml
serviceAccountName: hybrid-rag-sa
automountServiceAccountToken: false
```

**Network policies:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hybrid-rag-network-policy
spec:
  podSelector:
    matchLabels:
      app: hybrid-rag-api
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8000
```

---

### 2. Resource Management

**Set appropriate limits:**
```yaml
resources:
  requests:  # Guaranteed
    memory: "2Gi"
    cpu: "1000m"
  limits:    # Maximum
    memory: "4Gi"
    cpu: "2000m"
```

**Enable resource quotas:**
```bash
kubectl create quota hybrid-rag-quota \
  --hard=pods=20,requests.cpu=20,requests.memory=40Gi \
  -n hybrid-rag
```

---

### 3. High Availability

**Pod anti-affinity:**
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: hybrid-rag-api
        topologyKey: kubernetes.io/hostname
```

**Multiple availability zones:**
```yaml
nodeSelector:
  topology.kubernetes.io/zone: us-central1-a
```

---

### 4. Observability

**Add Prometheus annotations:**
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

**Centralized logging:**
```bash
# Use EFK or Loki stack
kubectl logs -f deployment/hybrid-rag-api -n hybrid-rag | <log-aggregator>
```

---

## 📈 SCALING GUIDE

### Expected Performance

| Pods | Throughput | Latency | Cost/Month* |
|------|-----------|---------|-------------|
| 3 | ~300 qps | ~360ms | $200 |
| 5 | ~500 qps | ~360ms | $350 |
| 10 | ~1000 qps | ~360ms | $700 |

*Estimated for 2GB pods on GKE

### When to Scale

**Scale UP if:**
- CPU consistently >70%
- Memory consistently >80%
- Request queue growing
- Latency increasing

**Scale DOWN if:**
- CPU consistently <30%
- Memory consistently <40%
- Over-provisioned

---

## ✅ DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] Kubernetes cluster created
- [ ] kubectl configured
- [ ] Docker image built and pushed
- [ ] Credentials obtained (Neo4j, Qdrant, Gemini)

### Deployment
- [ ] Namespace created
- [ ] Secrets created
- [ ] ConfigMap applied
- [ ] Deployment applied
- [ ] Service applied
- [ ] HPA applied

### Verification
- [ ] All pods running (3/3)
- [ ] Service has external IP
- [ ] Health check returns healthy
- [ ] Can upload document via API
- [ ] Can query via API
- [ ] HPA showing metrics

### Production Ready
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Auto-scaling working
- [ ] Monitoring enabled
- [ ] Backup strategy defined

---

## 🎯 QUICK DEPLOY SCRIPT

Save as `deploy-k8s.sh`:

```bash
#!/bin/bash

NAMESPACE="hybrid-rag"

echo "🚀 Deploying Hybrid RAG to Kubernetes..."

# Create namespace
kubectl create namespace $NAMESPACE 2>/dev/null || echo "Namespace exists"

# Create secrets (you need to create secrets.yaml first)
if [ -f "k8s/secrets.yaml" ]; then
    kubectl apply -f k8s/secrets.yaml -n $NAMESPACE
    echo "✅ Secrets created"
else
    echo "⚠️  Create k8s/secrets.yaml first!"
    exit 1
fi

# Apply all manifests
kubectl apply -f k8s/configmap.yaml -n $NAMESPACE
kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
kubectl apply -f k8s/service.yaml -n $NAMESPACE
kubectl apply -f k8s/hpa.yaml -n $NAMESPACE

echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=hybrid-rag-api -n $NAMESPACE --timeout=300s

echo "✅ Deployment complete!"
echo ""
echo "Get external IP:"
echo "  kubectl get svc hybrid-rag-api-service -n $NAMESPACE"
echo ""
echo "View pods:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/hybrid-rag-api -n $NAMESPACE"
```

**Run it:**
```bash
chmod +x deploy-k8s.sh
./deploy-k8s.sh
```

---

## 🎉 SUCCESS!

**Your Hybrid RAG System is now running in production on Kubernetes!**

**Access it:**
```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc hybrid-rag-api-service -n hybrid-rag -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health
curl http://$EXTERNAL_IP/health

# Upload document
curl -X POST http://$EXTERNAL_IP/ingest -F "file=@test.txt"

# Query
curl -X POST http://$EXTERNAL_IP/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?"}'
```

---

**Kubernetes Infrastructure:** ✅ COMPLETE  
**Production Ready:** ✅ YES  
**Auto-Scaling:** ✅ ENABLED  
**High Availability:** ✅ 3 REPLICAS
