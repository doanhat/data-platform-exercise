resource "google_cloudfunctions2_function" "preprocessing_function" {
  name        = local.preprocessing_function_name
  location    = local.gcp_region
  description = "Function pre-processing incoming transaction data"
  build_config {
    runtime = "python39"
    source {
      storage_source {
        bucket = google_storage_bucket.transaction_bucket.name
        object = google_storage_bucket_object.processor_code.name
      }
    }
    entry_point = local.preprocessing_function_entrypoint
  }
  service_config {
    environment_variables = {
      PROJECT_ID = local.project_id,
      TOPIC_NAME = local.in_progress_transaction_topic_name,
      DLQ_NAME = local.raw_transaction_dlq_name,
      EVENT_MAX_AGE = local.event_max_age,
    }
  }
  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.raw_transaction_topic.id
    retry_policy = "RETRY_POLICY_RETRY"
  }
}

resource "google_cloudfunctions2_function" "fee_processing_function" {
  name        = local.fee_processing_function_name
  location    = local.gcp_region
  description = "Function processing fee for in-progress transactions"
  build_config {
    runtime = "python39"
    source {
      storage_source {
        bucket = google_storage_bucket.transaction_bucket.name
        object = google_storage_bucket_object.processor_code.name
      }
    }
    entry_point = local.fee_processing_function_entrypoint
  }
  service_config {
    environment_variables = {
      PROJECT_ID = local.project_id,
      DLQ_NAME = local.in_progress_transaction_dlq_name,
      EVENT_MAX_AGE = local.event_max_age,
    }
  }
  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.in_progress_transaction_topic.id
    retry_policy = "RETRY_POLICY_RETRY"
  }
}