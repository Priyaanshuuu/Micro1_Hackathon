# Data Security & Hosting Policy

## Deployment Model
The Platform is delivered exclusively as multi-tenant SaaS hosted on public cloud infrastructure (AWS, us-east-1 and eu-west-1). **On-premise, self-hosted, or single-tenant dedicated deployments are not offered or supported.**

## Encryption in Transit
All data in transit is encrypted using TLS 1.2 or higher. Internal service-to-service traffic within the production network uses mutual TLS.

## Encryption at Rest
All customer data at rest is encrypted using AES-256. Keys are managed exclusively by the Platform's cloud KMS; **customer-managed encryption keys (CMEK/BYOK) are not currently supported** for production workloads. Keys rotate automatically every 90 days.

## Network Security
Production infrastructure sits in a private VPC with no direct public access to application servers or databases. External access passes through a WAF and load balancer with rate limiting and DDoS protection.

## Data Residency
Enterprise customers may select a US or EU hosting region at onboarding. Data does not leave that region except for encrypted DR backups replicated within the same jurisdiction (US↔US, EU↔EU).