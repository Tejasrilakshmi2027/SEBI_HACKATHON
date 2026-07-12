# SEBI Sentinel AI - Deployment Guide

This guide covers deploying SEBI Sentinel AI to production environments.

## Deployment Options

### Option 1: Docker Compose (Simplified Production)

Suitable for small to medium deployments.

#### Prerequisites
- Production server with Docker and Docker Compose installed
- Domain name configured
- SSL certificate (Let's Encrypt recommended)

#### Steps

1. **Prepare the Server**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Clone and Configure**

```bash
# Clone repository
git clone https://github.com/your-org/sebi-sentinel-ai.git
cd SEBI_project

# Copy environment file
cp .env.example .env
```

3. **Configure Production Environment**

Edit `.env` with production values:

```env
# Database Configuration
POSTGRES_USER=strong_password_here
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=sebi_db
DATABASE_URL=postgresql://user:password@postgres:5432/sebi_db

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=strong_username
MONGO_INITDB_ROOT_PASSWORD=strong_password
MONGODB_URL=mongodb://user:password@mongodb:27017

# Redis Configuration
REDIS_URL=redis://:password@redis:6379

# Application Configuration
SECRET_KEY=generate-random-256-bit-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760

# Frontend Configuration
VITE_API_URL=https://api.yourdomain.com
```

4. **Generate SSL Certificate**

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

5. **Update Nginx Configuration**

Edit `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **Deploy**

```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f
```

### Option 2: Cloud Deployment (AWS)

Suitable for scalable, production-grade deployments.

#### Architecture

```
┌─────────────────────────────────────────┐
│           AWS CloudFront (CDN)           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│            AWS Application Load Balancer │
└─────────┬───────────────────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Backend ECS    │     │  Frontend S3    │
│  (FastAPI)      │     │  + CloudFront   │
└────────┬────────┘     └─────────────────┘
         │
         ├─────────────────┬────────────────┐
         │                 │                │
         ▼                 ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   RDS        │  │  DocumentDB  │  │   ElastiCache│
│ (PostgreSQL) │  │  (MongoDB)   │  │   (Redis)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

#### Steps

1. **Create VPC and Networking**

```bash
# Using AWS CLI
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24
aws ec2 create-security-group --group-name sebi-sg --description "SEBI Sentinel Security Group"
```

2. **Set Up RDS (PostgreSQL)**

```bash
aws rds create-db-instance \
  --db-instance-identifier sebi-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 20 \
  --vpc-security-group-ids <sg-id> \
  --db-subnet-group-name <subnet-group>
```

3. **Set Up DocumentDB (MongoDB)**

```bash
aws docdb create-db-cluster \
  --db-cluster-identifier sebi-mongodb \
  --master-username admin \
  --master-user-password <password> \
  --vpc-security-group-ids <sg-id>

aws docdb create-db-instance \
  --db-cluster-identifier sebi-mongodb \
  --db-instance-class db.t3.medium
```

4. **Set Up ElastiCache (Redis)**

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id sebi-redis \
  --engine redis \
  --cache-node-type cache.t3.medium \
  --num-cache-nodes 1 \
  --security-group-ids <sg-id>
```

5. **Build and Push Docker Images**

```bash
# Login to ECR
aws ecr get-login-password --region | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Build backend image
docker build -t sebi-backend ./backend
docker tag sebi-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/sebi-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/sebi-backend:latest

# Build frontend image
docker build -t sebi-frontend ./frontend
docker tag sebi-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/sebi-frontend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/sebi-frontend:latest
```

6. **Deploy to ECS**

Create ECS task definitions and services using AWS Console or CLI.

7. **Configure Application Load Balancer**

Set up ALB with SSL certificates and route traffic to ECS.

8. **Deploy Frontend to S3**

```bash
# Build frontend
cd frontend
npm run build

# Upload to S3
aws s3 sync dist s3://sebi-frontend-bucket

# Configure CloudFront distribution
aws cloudfront create-distribution --distribution-config <config-file>
```

### Option 3: Kubernetes (EKS/GKE)

Suitable for large-scale, highly available deployments.

#### Prerequisites
- Kubernetes cluster (EKS, GKE, or self-managed)
- kubectl configured
- Helm installed

#### Steps

1. **Create Kubernetes Namespace**

```bash
kubectl create namespace sebi-sentinel
```

2. **Create Secrets**

```bash
kubectl create secret generic sebi-secrets \
  --from-literal=database-url=<db-url> \
  --from-literal=mongodb-url=<mongo-url> \
  --from-literal=redis-url=<redis-url> \
  --from-literal=secret-key=<secret-key> \
  -n sebi-sentinel
```

3. **Deploy PostgreSQL**

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql -n sebi-sentinel
```

4. **Deploy MongoDB**

```bash
helm install mongodb bitnami/mongodb -n sebi-sentinel
```

5. **Deploy Redis**

```bash
helm install redis bitnami/redis -n sebi-sentinel
```

6. **Deploy Backend**

Create `backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sebi-backend
  namespace: sebi-sentinel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sebi-backend
  template:
    metadata:
      labels:
        app: sebi-backend
    spec:
      containers:
      - name: backend
        image: <your-registry>/sebi-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: sebi-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: sebi-backend
  namespace: sebi-sentinel
spec:
  selector:
    app: sebi-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

Apply deployment:
```bash
kubectl apply -f backend-deployment.yaml
```

7. **Deploy Frontend**

Create `frontend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sebi-frontend
  namespace: sebi-sentinel
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sebi-frontend
  template:
    metadata:
      labels:
        app: sebi-frontend
    spec:
      containers:
      - name: frontend
        image: <your-registry>/sebi-frontend:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: sebi-frontend
  namespace: sebi-sentinel
spec:
  selector:
    app: sebi-frontend
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

Apply deployment:
```bash
kubectl apply -f frontend-deployment.yaml
```

8. **Configure Ingress**

Create `ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sebi-ingress
  namespace: sebi-sentinel
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: sebi-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: sebi-backend
            port:
              number: 8000
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sebi-frontend
            port:
              number: 80
```

Apply ingress:
```bash
kubectl apply -f ingress.yaml
```

## Monitoring and Logging

### Application Monitoring

Install Prometheus and Grafana:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

### Log Aggregation

Install ELK Stack or Loki:

```bash
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n logging
helm install kibana elastic/kibana -n logging
```

## Backup Strategy

### Database Backups

**PostgreSQL:**
```bash
# Automated backups via AWS RDS
aws rds create-db-snapshot --db-instance-identifier sebi-postgres --db-snapshot-id sebi-backup-$(date +%Y%m%d)
```

**MongoDB:**
```bash
# Automated backups via AWS DocumentDB
aws docdb create-db-cluster-snapshot --db-cluster-identifier sebi-mongodb --db-cluster-snapshot-identifier sebi-backup-$(date +%Y%m%d)
```

### File Storage Backups

Configure S3 versioning or use backup services like AWS Backup.

## Security Hardening

### Firewall Rules
- Restrict access to database ports
- Only allow HTTPS traffic
- Implement IP whitelisting for admin access

### SSL/TLS
- Use strong TLS 1.2+ ciphers
- Enable HSTS
- Implement certificate auto-renewal

### Application Security
- Enable rate limiting
- Implement request validation
- Use security headers
- Regular dependency updates

## CI/CD Pipeline

See `.github/workflows/ci-cd.yml` for automated deployment configuration.

## Scaling

### Horizontal Scaling

Increase replica count in Kubernetes or ECS:

```bash
kubectl scale deployment sebi-backend --replicas=5 -n sebi-sentinel
```

### Vertical Scaling

Increase resource limits in deployment configuration.

### Auto-scaling

Configure Horizontal Pod Autoscaler (HPA):

```bash
kubectl autoscale deployment sebi-backend --cpu-percent=70 --min=3 --max=10 -n sebi-sentinel
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n sebi-sentinel
kubectl describe pod <pod-name> -n sebi-sentinel
kubectl logs <pod-name> -n sebi-sentinel
```

### Check Service Status
```bash
kubectl get services -n sebi-sentinel
kubectl describe service <service-name> -n sebi-sentinel
```

### Check Ingress
```bash
kubectl get ingress -n sebi-sentinel
kubectl describe ingress <ingress-name> -n sebi-sentinel
```

## Rollback

### Docker Compose
```bash
docker-compose down
docker-compose up -d --build
```

### Kubernetes
```bash
kubectl rollout undo deployment sebi-backend -n sebi-sentinel
```

## Performance Optimization

### Database Optimization
- Configure connection pooling
- Enable query caching
- Use read replicas for read-heavy workloads

### Caching Strategy
- Implement Redis caching for frequently accessed data
- Cache API responses
- Use CDN for static assets

### Load Balancing
- Distribute traffic across multiple instances
- Implement health checks
- Configure session affinity if needed
