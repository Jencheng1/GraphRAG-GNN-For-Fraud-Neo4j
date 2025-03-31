terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudrun.googleapis.com",
    "sqladmin.googleapis.com",
    "artifactregistry.googleapis.com",
    "containerregistry.googleapis.com",
    "compute.googleapis.com",
    "cloudbuild.googleapis.com"
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}

# Create VPC network
resource "google_compute_network" "vpc" {
  name                    = "credit-fraud-vpc"
  auto_create_subnetworks = true
}

# Create Cloud SQL instance for PostgreSQL
resource "google_sql_database_instance" "postgres" {
  name             = "credit-fraud-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc.id
    }
    backup_configuration {
      enabled = true
    }
    database_flags {
      name  = "max_connections"
      value = "1000"
    }
  }
}

# Create Cloud SQL instance for Neo4j
resource "google_compute_instance" "neo4j" {
  name         = "credit-fraud-neo4j"
  machine_type = "e2-medium"
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 50
    }
  }

  network_interface {
    network = google_compute_network.vpc.name
    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = file("${path.module}/scripts/neo4j_startup.sh")
}

# Create Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "credit-fraud-repo"
  description   = "Docker repository for credit fraud detection"
  format        = "DOCKER"
}

# Create Cloud Run service for backend
resource "google_cloud_run_service" "backend" {
  name     = "credit-fraud-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/credit-fraud-repo/backend:latest"
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_user}:${var.db_password}@${google_sql_database_instance.postgres.connection_name}/credit_fraud"
        }
        
        env {
          name  = "NEO4J_URI"
          value = "bolt://${google_compute_instance.neo4j.network_interface[0].access_config[0].nat_ip}:7687"
        }
        
        env {
          name  = "NEO4J_USER"
          value = "neo4j"
        }
        
        env {
          name  = "NEO4J_PASSWORD"
          value = var.neo4j_password
        }
        
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Create Cloud Run service for frontend
resource "google_cloud_run_service" "frontend" {
  name     = "credit-fraud-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/credit-fraud-repo/frontend:latest"
        
        env {
          name  = "REACT_APP_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Create Cloud Build trigger for backend
resource "google_cloudbuild_trigger" "backend_trigger" {
  name        = "credit-fraud-backend-trigger"
  description = "Trigger for building and deploying backend"
  filename    = "cloudbuild.yaml"
  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }
}

# Create Cloud Build trigger for frontend
resource "google_cloudbuild_trigger" "frontend_trigger" {
  name        = "credit-fraud-frontend-trigger"
  description = "Trigger for building and deploying frontend"
  filename    = "cloudbuild.yaml"
  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }
} 