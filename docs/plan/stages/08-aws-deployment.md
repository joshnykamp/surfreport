# 08 AWS deployment

**Status:** Not started (not needed until the app works locally)

## Goal
Run the app and the scheduled forecast job in AWS for under $50 to $60 a month, fully managed with Terraform.

## Architecture
- ECR for container images
- ECS Fargate service running the FastAPI app (0.25 vCPU, 0.5 GB to start)
- Application Load Balancer: deferred; reach the task directly at first and add an ALB or CloudFront later
- EventBridge Scheduler starting a Fargate task for the forecast refresh every 6 hours
- RDS Postgres, single AZ, db.t4g.micro
- Secrets Manager for the database password and LLM API key
- CloudWatch Logs for the app and the job
- No NAT gateway: public subnets with tight security groups

## Rough monthly cost (verify with the AWS Pricing Calculator)
| Item | Approx. |
|---|---|
| Fargate service, always on | $9 |
| RDS db.t4g.micro + 20 GB storage | $14 to $16 |
| Public IPv4 addresses | $4 to $8 |
| Secrets Manager, ECR, CloudWatch, scheduled tasks | $3 to $5 |
| **Total** | **about $30 to $40** (add $16 to $18 with an ALB) |

LLM API costs are separate and depend on the model and number of spots.

## Kubernetes
Local only for now, using the Kubernetes built into Docker Desktop. Keep Kubernetes manifests in the repo. EKS (about $73 a month for the control plane alone) is a possible later stage and does not fit this budget.

## Acceptance criteria
- [ ] Terraform state stored in S3 with locking
- [ ] `terraform apply` creates everything from scratch; `terraform destroy` removes it
- [ ] App reachable (HTTPS once an ALB or CloudFront is added)
- [ ] Forecast job runs every 6 hours and logs to CloudWatch
- [ ] No secrets in the repo or in Terraform state outputs
- [ ] AWS Budgets alert set at $50

## Tasks
- [ ] S3 bucket for Terraform state
- [ ] Network: VPC, public subnets, security groups
- [ ] ECR repository and image build
- [ ] RDS instance and Secrets Manager secret
- [ ] ECS cluster, task definitions and service
- [ ] EventBridge schedule for the refresh job
- [ ] Budget alert

## Open questions
- Domain name and HTTPS certificate (ACM is free, a domain is about $12 to $15 a year)
- When to add the ALB, and ALB vs CloudFront
