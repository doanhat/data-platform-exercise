resource "google_cloud_run_v2_service" "monthly_billing_processing_service" {
  location = local.gcp_region
  name     = local.monthly_fee_processing_service_name
  template {
    timeout = "3600s"
    containers {
      image = "${local.gcp_region}-docker.pkg.dev/${local.project_id}/${local.monthly_fee_processing_service_repo}/cloud_run_service${var.docker_version}"
      ports {
        container_port = 8080
      }
    }
  }
  deletion_protection = false
}

variable "docker_version" {
  type = string
}