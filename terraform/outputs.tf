output "frontend_url" {
  description = "The URL of the deployed frontend application"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "backend_url" {
  description = "The URL of the deployed backend API"
  value       = google_cloud_run_service.backend.status[0].url
}

output "neo4j_instance_ip" {
  description = "The IP address of the Neo4j instance"
  value       = google_compute_instance.neo4j.network_interface[0].access_config[0].nat_ip
}

output "postgres_instance_connection_name" {
  description = "The connection name of the PostgreSQL instance"
  value       = google_sql_database_instance.postgres.connection_name
}

output "artifact_registry_repository" {
  description = "The name of the Artifact Registry repository"
  value       = google_artifact_registry_repository.repo.name
} 