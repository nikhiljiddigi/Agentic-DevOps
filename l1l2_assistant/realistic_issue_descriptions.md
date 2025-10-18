# 🧠 Realistic Infrastructure & Application Issue Descriptions

A unified collection of realistic production issue scenarios across DevOps, SRE, and platform engineering domains — designed for automated L1/L2 triage and RCA reasoning.

---

## ⚡ Payment API latency increase during traffic surge

### Description
Payment API response time spiked from 350 ms → 2.3 s during a traffic surge.

### Observations
- Average CPU utilization normal (55%), but DB query latency increased 4×.  
- Autoscaler did not trigger additional pods.  
- Connection pool near saturation (`maxActiveConnections = 50`).  
- API pods logging slow queries involving joins on `transactions` table.

### Logs
```
WARN Slow query detected (duration: 2100ms)
SELECT * FROM transactions INNER JOIN refunds ...
```

### Impact
Checkout flow degraded for ~30 % of users.

---

## 🧩 Redis cache inconsistency between regions

### Description
Stale cache data observed between `us-east` and `eu-west` clusters.

### Observations
- Redis replication lag ≈ 45 seconds.  
- Primary node CPU at 90 %.  
- Recent config update changed `replica-read-only` flag to false.  
- No failover events recorded.

### Logs
```
WARN replication buffer backlog too long (current 30MB)
```

### Impact
Users in EU region seeing outdated order statuses.

---

## 🧱 CI/CD pipeline stuck during artifact upload

### Description
Build pipeline job stuck during artifact upload to Nexus repository.

### Observations
- Upload step running > 15 minutes without progress.  
- Nexus logs show intermittent 500 responses.  
- Runners operating normally; network bandwidth low.  
- Recent Nexus upgrade deployed (v3.60 → v3.61).

### Logs
```
[ERROR] Failed to transfer file: HTTP 500 Internal Server Error
```

### Impact
New builds blocked; deployment delayed.

---

## 🔒 Expired API token causing service authentication failures

### Description
Requests from `billing-svc` to `auth-svc` failing with 401 Unauthorized errors.

### Observations
- JWT token expired at 03:00 UTC.  
- No automatic token refresh job triggered.  
- Secrets in Vault unchanged since last week.  
- `auth-svc` healthy; no downtime reported.

### Logs
```
ERROR Authentication failed: token expired
```

### Impact
Billing API requests failing; background job retries accumulating.

---

## 🌐 Intermittent DNS resolution errors in internal services

### Description
Some internal microservices failing DNS lookups for cluster-local endpoints.

### Observations
- Errors only on `node-group-b`.  
- CoreDNS pods restarted recently after memory spike.  
- Logs show repeated upstream timeout warnings.  
- Kubelet and node network CNI versions mismatched.

### Logs
```
E1018 12:10:35.231 resolver.go:148] DNS lookup failed for auth.internal.local: timeout
```

### Impact
Intermittent failures in authentication and session APIs.

---

## 🧮 Incorrect autoscaling thresholds causing over-provisioning

### Description
Autoscaler adding 10+ unnecessary pods for `search-svc` despite low traffic.

### Observations
- HPA threshold misconfigured (`targetCPUUtilization=10`).  
- CPU usage steady at 20 %, but still triggering scale-up.  
- No custom metrics applied.  
- Cluster CPU quota nearing limits.

### Logs
```
INFO HPA scaling from 4 → 16 replicas (CPU=18%)
```

### Impact
Unnecessary cost increase; 4× pod count with no demand.

---

## 🧱 Deployment misconfiguration after Helm chart update

### Description
Recent Helm chart upgrade introduced incorrect environment variable values.

### Observations
- `configmap` mismatch between staging and prod.  
- Variable `PAYMENT_GATEWAY_URL` missing in prod template.  
- Rollback fixed deployment instantly.  
- No image or code changes involved.

### Logs
```
ERROR Failed to initialize gateway client: missing URL configuration
```

### Impact
Payment API unavailable for 10 minutes post-deploy.

---

## 🧊 SSL handshake failures with external dependency

### Description
Outbound requests from `inventory-svc` to third-party API failing SSL handshake.

### Observations
- Root CA bundle expired inside container image.  
- cURL verification fails with `certificate verify failed`.  
- No proxy or firewall issues.  
- Image base not rebuilt in 3 months.

### Logs
```
curl: (60) SSL certificate problem: certificate has expired
```

### Impact
Integration with vendor API unavailable.

---

## 💾 PostgreSQL replication lag in standby region

### Description
Standby PostgreSQL replica in `ap-south-1` lagging behind primary by 10+ minutes.

### Observations
- WAL receiver stuck due to slow I/O on replica node.  
- No network errors detected.  
- Recent maintenance reduced disk IOPS quota.  
- Monitoring shows consistent lag trend.

### Logs
```
WARNING: WAL receiver terminated: requested WAL segment 00000001000000A5 not yet available
```

### Impact
Read traffic served from stale replica; analytics data delayed.
