resource "google_workflows_workflow" "workflow" {
  name   = local.workflow_name
  region = local.gcp_region
  source_contents = templatefile("../../workflow/workflow.yaml", {
    location = local.gcp_region
    invoke_url = google_cloud_run_v2_service.monthly_billing_processing_service.uri
    bucket_name = google_storage_bucket.transaction_bucket.name
    dataflow_job_name = local.dataflow_job_name
  })
}

resource "google_cloud_scheduler_job" "workflow_schedule" {
  name             = local.scheduler_name
  description      = "Cloud Scheduler for Workflow Job"
  schedule         = local.scheduler_cron
  time_zone        = local.scheduler_tz
  attempt_deadline = local.scheduler_attempt
  region           = local.gcp_region

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.workflow.id}/executions"
    body = base64encode(
      jsonencode({
        "callLogLevel" : "CALL_LOG_LEVEL_UNSPECIFIED"
        }
    ))

    oauth_token {
      service_account_email = "885070032799-compute@developer.gserviceaccount.com"
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }

}