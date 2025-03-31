# Credit Fraud Detection - GCP Deployment

This directory contains the Terraform configuration for deploying the Credit Fraud Detection application to Google Cloud Platform.

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. [Terraform](https://www.terraform.io/downloads.html) installed (version >= 1.0)
3. A Google Cloud Project with billing enabled
4. Service account with necessary permissions

## Setup

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Create a `terraform.tfvars` file with your configuration:
   ```hcl
   project_id = "your-project-id"
   region     = "us-central1"
   db_user    = "postgres"
   db_password = "your-secure-password"
   neo4j_password = "your-secure-password"
   openai_api_key = "your-openai-api-key"
   github_owner = "your-github-username"
   github_repo = "credit-fraud-detection"
   ```

3. Enable required APIs in your GCP project:
   ```bash
   gcloud services enable \
     run.googleapis.com \
     sqladmin.googleapis.com \
     artifactregistry.googleapis.com \
     cloudbuild.googleapis.com
   ```

## Deployment

1. Review the planned changes:
   ```bash
   terraform plan
   ```

2. Apply the configuration:
   ```bash
   terraform apply
   ```

3. After deployment, Terraform will output:
   - Frontend URL
   - Backend API URL
   - Neo4j instance IP
   - PostgreSQL connection name
   - Artifact Registry repository name

## Infrastructure Components

The deployment creates the following resources:

1. **VPC Network**
   - Custom network for the application
   - Firewall rules for Neo4j access

2. **Cloud SQL (PostgreSQL)**
   - Managed PostgreSQL instance
   - Automated backups
   - Private IP configuration

3. **Compute Engine (Neo4j)**
   - VM instance for Neo4j database
   - Startup script for Neo4j installation
   - External IP for access

4. **Cloud Run Services**
   - Backend API service
   - Frontend application service
   - Container images stored in Artifact Registry

5. **Cloud Build Triggers**
   - Automated builds on GitHub pushes
   - Separate triggers for frontend and backend

## Maintenance

### Updating Infrastructure

1. Make changes to the Terraform configuration files
2. Review changes:
   ```bash
   terraform plan
   ```
3. Apply changes:
   ```bash
   terraform apply
   ```

### Scaling

- Cloud Run services automatically scale based on traffic
- PostgreSQL instance can be resized by updating the `tier` variable
- Neo4j instance can be resized by updating the `machine_type` variable

### Monitoring

- Use Cloud Monitoring for metrics and alerts
- Cloud Logging for application logs
- Cloud Trace for request tracing

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Note**: This will delete all resources, including databases. Make sure to backup any important data before running this command.

## Security Considerations

1. All sensitive variables are marked as sensitive in Terraform
2. Database passwords are stored securely in Cloud Run environment variables
3. Neo4j instance is protected by firewall rules
4. PostgreSQL instance uses private IP
5. Cloud Run services are configured with appropriate IAM permissions

## Troubleshooting

1. Check Cloud Build logs for deployment issues
2. Review Cloud Run service logs for application errors
3. Verify database connectivity using Cloud SQL proxy
4. Check firewall rules for Neo4j access issues 