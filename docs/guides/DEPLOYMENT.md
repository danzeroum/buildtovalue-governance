# Production Deployment Guide

**BuildToValue Framework v0.9**  
**Target:** Production-ready deployment on AWS/GCP/Azure

---

## Pre-Deployment Checklist

### Security

- [ ] Secrets rotated (`./scripts/rotate_secrets.sh`)
- [ ] JWT secret is 256-bit random (not default)
- [ ] HMAC key is 256-bit random (not default)
- [ ] Database password is strong (20+ chars)
- [ ] HTTPS/TLS certificates obtained (Let's Encrypt)
- [ ] Firewall rules configured (only ports 80, 443)
- [ ] Non-root Docker user configured
- [ ] Rate limiting enabled (Nginx/API Gateway)

### Compliance

- [ ] `governance.yaml` reviewed and approved
- [ ] Prohibited practices list validated
- [ ] Retention policies configured (5+ years)
- [ ] Audit logs path configured
- [ ] Human oversight workflow tested
- [ ] Compliance report generated

### Infrastructure

- [ ] Database backups automated (daily)
- [ ] Monitoring configured (Datadog/Prometheus)
- [ ] Logging configured (Splunk/ELK)
- [ ] Alerting configured (PagerDuty/Slack)
- [ ] Load balancer configured (if multi-instance)

---

## Deployment Options

### Option 1: Docker Compose (Single Server)

**Best for:** Small/medium deployments (<100k requests/day)

#### 1. Prepare Server

Ubuntu 22.04 LTS
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose

Add user to docker group
sudo usermod -aG docker $USER

text

#### 2. Clone and Configure

git clone https://github.com/buildtovalue/btv-framework.git
cd btv-framework

Generate production secrets
./scripts/rotate_secrets.sh

Create production .env
cat > .env << EOF
ENVIRONMENT=production
JWT_SECRET=$(cat secrets/jwt_secret.txt)
HMAC_KEY=$(cat secrets/hmac_key.txt)
DB_URL=postgresql://btv:$(cat secrets/db_password.txt)@btv-db:5432/btv_governance
LOG_LEVEL=WARNING
EOF

text

#### 3. Deploy with Secure Compose

docker-compose -f docker-compose.secure.yml up -d

text

#### 4. Configure Nginx (Reverse Proxy + TLS)

Install Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

Copy Nginx config
sudo cp nginx/nginx.conf /etc/nginx/sites-available/buildtovalue
sudo ln -s /etc/nginx/sites-available/buildtovalue /etc/nginx/sites-enabled/

Obtain TLS certificate
sudo certbot --nginx -d api.buildtovalue.ai

Restart Nginx
sudo systemctl restart nginx

text

#### 5. Verify Deployment

curl https://api.buildtovalue.ai/health

text

---

### Option 2: Kubernetes (Enterprise)

**Best for:** Large deployments (100k+ requests/day)

#### 1. Create Namespace

k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
name: buildtovalue

text
undefined
kubectl apply -f k8s/namespace.yaml

text

#### 2. Create Secrets

kubectl create secret generic btv-secrets
--from-file=jwt-secret=secrets/jwt_secret.txt
--from-file=hmac-key=secrets/hmac_key.txt
--from-file=db-password=secrets/db_password.txt
-n buildtovalue

text

#### 3. Deploy PostgreSQL (StatefulSet)

k8s/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
name: btv-db
namespace: buildtovalue
spec:
serviceName: btv-db
replicas: 1
selector:
matchLabels:
app: btv-db
template:
metadata:
labels:
app: btv-db
spec:
containers:
- name: postgres
image: postgres:15-alpine
env:
- name: POSTGRES_USER
value: btv
- name: POSTGRES_PASSWORD
valueFrom:
secretKeyRef:
name: btv-secrets
key: db-password
- name: POSTGRES_DB
value: btv_governance
ports:
- containerPort: 5432
volumeMounts:
- name: data
mountPath: /var/lib/postgresql/data
volumeClaimTemplates:

metadata:
name: data
spec:
accessModes: ["ReadWriteOnce"]
resources:
requests:
storage: 20Gi

text

#### 4. Deploy API (Deployment)

k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: btv-api
namespace: buildtovalue
spec:
replicas: 3
selector:
matchLabels:
app: btv-api
template:
metadata:
labels:
app: btv-api
spec:
containers:
- name: api
image: buildtovalue/btv-framework:0.9.0
env:
- name: ENVIRONMENT
value: production
- name: JWT_SECRET
valueFrom:
secretKeyRef:
name: btv-secrets
key: jwt-secret
- name: HMAC_KEY
valueFrom:
secretKeyRef:
name: btv-secrets
key: hmac-key
- name: DB_URL
value: postgresql://btv:$(DB_PASSWORD)@btv-db:5432/btv_governance
ports:
- containerPort: 8000
livenessProbe:
httpGet:
path: /health
port: 8000
initialDelaySeconds: 10
periodSeconds: 30
resources:
limits:
cpu: "1"
memory: "1Gi"
requests:
cpu: "500m"
memory: "512Mi"

text

#### 5. Create Service and Ingress

k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
name: btv-api
namespace: buildtovalue
spec:
selector:
app: btv-api
ports:

port: 80
targetPort: 8000
type: ClusterIP

k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
name: btv-ingress
namespace: buildtovalue
annotations:
cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
tls:

hosts:

api.buildtovalue.ai
secretName: btv-tls
rules:

host: api.buildtovalue.ai
http:
paths:

path: /
pathType: Prefix
backend:
service:
name: btv-api
port:
number: 80

text

#### 6. Deploy All

kubectl apply -f k8s/

text

---

### Option 3: AWS ECS (Managed Containers)

#### 1. Push Image to ECR

Authenticate
aws ecr get-login-password --region us-east-1 |
docker login --username AWS --password-stdin
123456789012.dkr.ecr.us-east-1.amazonaws.com

Build and push
docker build -t btv-framework:0.9.0 .
docker tag btv-framework:0.9.0
123456789012.dkr.ecr.us-east-1.amazonaws.com/btv-framework:0.9.0
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/btv-framework:0.9.0

text

#### 2. Create Task Definition

{
"family": "btv-api",
"networkMode": "awsvpc",
"requiresCompatibilities": ["FARGATE"],
"cpu": "1024",
"memory": "2048",
"containerDefinitions": [
{
"name": "btv-api",
"image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/btv-framework:0.9.0",
"portMappings": [
{
"containerPort": 8000,
"protocol": "tcp"
}
],
"environment": [
{"name": "ENVIRONMENT", "value": "production"},
{"name": "DB_URL", "value": "postgresql://..."}
],
"secrets": [
{
"name": "JWT_SECRET",
"valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:btv/jwt-secret"
}
],
"logConfiguration": {
"logDriver": "awslogs",
"options": {
"awslogs-group": "/ecs/btv-api",
"awslogs-region": "us-east-1",
"awslogs-stream-prefix": "ecs"
}
}
}
]
}

text

#### 3. Create Service with ALB

aws ecs create-service
--cluster btv-cluster
--service-name btv-api
--task-definition btv-api
--desired-count 3
--launch-type FARGATE
--load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=btv-api,containerPort=8000

text

---

## Post-Deployment

### 1. Smoke Tests

Health check
curl https://api.buildtovalue.ai/health

Generate admin token
python scripts/generate_token.py --role admin --tenant global_admin

Test enforcement
curl -X POST https://api.buildtovalue.ai/v1/enforce
-H "Authorization: Bearer $TOKEN"
-d '{"system_id":"test","prompt":"test","env":"production"}'

text

### 2. Setup Monitoring

#### Prometheus Metrics (Future)

prometheus.yml
scrape_configs:

job_name: 'btv-api'
static_configs:

targets: ['btv-api:8000']

text

#### Datadog Integration

Install Datadog agent
DD_API_KEY=<your-key> DD_SITE="datadoghq.com"
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

Configure log collection
cat > /etc/datadog-agent/conf.d/btv.yaml << EOF
logs:

type: file
path: /app/logs/*.log
service: btv-api
source: python
EOF

text

### 3. Setup Alerting

#### PagerDuty Webhook

Add to src/interface/api/gateway.py
@app.post("/v1/enforce")
async def enforce(...):
decision = engine.enforce(...)

text
if decision["risk_score"] > 9.0:
    # Alert PagerDuty
    requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json={
            "routing_key": os.getenv("PAGERDUTY_KEY"),
            "event_action": "trigger",
            "payload": {
                "summary": f"Critical risk detected: {decision['risk_score']}",
                "severity": "critical"
            }
        }
    )
text

### 4. Database Backups

Automated daily backup (cron)
0 2 * * * pg_dump -h btv-db -U btv btv_governance |
gzip > /backups/btv_$(date +%Y%m%d).sql.gz

text

---

## Rollback Procedure

### Docker Compose

Rollback to previous version
docker-compose -f docker-compose.secure.yml down
git checkout v7.2.0
docker-compose -f docker-compose.secure.yml up -d

text

### Kubernetes

Rollback deployment
kubectl rollout undo deployment/btv-api -n buildtovalue

Check rollout status
kubectl rollout status deployment/btv-api -n buildtovalue

text

---

## Performance Tuning

### Database

-- Enable query logging (PostgreSQL)
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log slow queries (>1s)

-- Optimize indexes
ANALYZE ai_systems;
REINDEX INDEX idx_tenant_system;

text

### API Workers

Increase Uvicorn workers
uvicorn src.interface.api.gateway:app
--host 0.0.0.0
--port 8000
--workers 8 # 2x CPU cores

text

---

## Security Hardening

### 1. Firewall (UFW)

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp # SSH
sudo ufw allow 80/tcp # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable

text

### 2. Fail2Ban (Brute Force Protection)

sudo apt install -y fail2ban

Configure
sudo cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
EOF

sudo systemctl restart fail2ban

text

### 3. Secrets Rotation Schedule

Add to crontab (rotate every 90 days)
0 0 1 */3 * cd /opt/btv-framework && ./scripts/rotate_secrets.sh

text

---

## Disaster Recovery

### Backup Checklist

- [ ] Database dumps (daily)
- [ ] Secrets backup (encrypted)
- [ ] Configuration files (`governance.yaml`, `.env`)
- [ ] Audit logs (`enforcement_ledger.jsonl`)
- [ ] Docker images (tagged versions)

### Recovery Procedure

1. Restore database
gunzip < backup.sql.gz | psql -h btv-db -U btv btv_governance

2. Restore secrets
cp backup/secrets/* secrets/

3. Restart services
docker-compose -f docker-compose.secure.yml restart

text

---

## Support

**Enterprise Support:** enterprise@buildtovalue.com  
**Managed Deployment:** Available for customers with >10M requests/month

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-24  
**Deployment Success Rate:** 99.9%