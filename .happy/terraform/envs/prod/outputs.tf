output "service_endpoints" {
  value       = module.stack.service_endpoints
  description = "The URL endpoints for the services"
  sensitive   = false
}

output "k8s_namespace" {
  value = data.kubernetes_namespace.happy-namespace.metadata.0.name
}

output "service_ecrs" {
  value = module.stack.service_ecrs
  description = "The services ECR locations for their docker containers"
  sensitive = false
}

