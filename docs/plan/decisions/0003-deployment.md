# 0003 Deployment, infrastructure and database

**Status:** Decided
**Date:** 2026-11-07

## Context
The app needs a web API, a scheduled forecast job every 6 hours, a Postgres database and secret storage. A secondary goal is to use AWS services broadly, along with Terraform and Kubernetes.

## Decision
- **Cloud:** AWS
- **App:** FastAPI in a Docker container on ECS Fargate
- **Refresh job:** EventBridge Scheduler starting a Fargate task every 6 hours
- **Database:** RDS Postgres, single AZ; Postgres in Docker Compose locally
- **ORM and migrations:** SQLAlchemy and Alembic (same migrations locally and on RDS)
- **Secrets:** AWS Secrets Manager
- **Infrastructure as code:** Terraform
- **Container registry:** ECR
- **Local containers:** Docker Desktop
- **Kubernetes:** local only (Docker Desktop), manifests in the repo; EKS possibly later
- **Budget:** under $50 to $60 a month (see stage 08)

## Cost notes
- Avoid a NAT gateway (about $30 a month on its own). Use public subnets with tight security groups, or VPC endpoints.
- EKS costs about $73 a month for the control plane alone, before any nodes.

## Open questions
- Keep or drop the load balancer (see stage 08)
