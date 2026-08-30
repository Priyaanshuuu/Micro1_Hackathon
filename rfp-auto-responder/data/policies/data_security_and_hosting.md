# Data Security and Hosting

## Hosting Model
Our platform operates as a **multi-tenant SaaS solution** hosted exclusively on cloud infrastructure. We do not offer on-premise deployments, self-hosted installations, or single-tenant dedicated environments.

All customer data is hosted on **AWS (Amazon Web Services)** infrastructure in the us-east-1 and eu-west-1 regions, depending on customer preference selected during onboarding.

## Encryption at Rest
All customer data stored in our production databases and object storage is encrypted at rest using **AES-256 encryption**. Encryption keys are managed by AWS Key Management Service (KMS) using **AWS-managed keys**.

We do **not** support customer-managed encryption keys (BYOK/CMEK) at this time. All encryption key lifecycle management is handled by our cloud provider.

## Encryption in Transit
All data transmission between client applications and our API endpoints uses **TLS 1.2 or higher**. We enforce HTTPS for all connections and do not support unencrypted HTTP traffic.

Internal communication between microservices within our AWS VPC also uses TLS encryption.

## Network Security
Production infrastructure resides in private subnets within AWS VPCs with no direct internet exposure. Public access is limited to our API Gateway and CDN endpoints, both protected by AWS WAF (Web Application Firewall) rules.

Database instances are accessible only from application servers within the VPC and require IAM-based authentication.

## Data Residency
Customers can select their primary data region (US or EU) during account setup. Once selected, all customer data remains within that geographic region and is not replicated cross-region without explicit customer consent.
