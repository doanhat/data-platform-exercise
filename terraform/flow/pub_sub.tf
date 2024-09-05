resource "google_pubsub_topic" "raw_transaction_topic" {
  name = local.raw_transaction_topic_name
}
resource "google_pubsub_topic" "raw_transaction_dlq" {
  name = local.raw_transaction_dlq_name
}
resource "google_pubsub_subscription" "raw_transaction_subscription" {
  name  = local.raw_transaction_subscription_name
  topic = google_pubsub_topic.raw_transaction_dlq.name

  # Define the dead letter policy
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.raw_transaction_dlq.id
    max_delivery_attempts = 5
  }

  # Define the acknowledgment deadline and message retention duration
  ack_deadline_seconds       = 20
  message_retention_duration = "86400s" # 1 day

  # Define the retry policy
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}


resource "google_pubsub_topic" "in_progress_transaction_topic" {
  name = local.in_progress_transaction_topic_name
}
resource "google_pubsub_topic" "in_progress_transaction_dlq" {
  name = local.in_progress_transaction_dlq_name
}
resource "google_pubsub_subscription" "in_progress_transaction_subscription" {
  name  = local.in_progress_transaction_subscription_name
  topic = google_pubsub_topic.in_progress_transaction_dlq.name

  # Define the dead letter policy
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.in_progress_transaction_dlq.id
    max_delivery_attempts = 5
  }

  # Define the acknowledgment deadline and message retention duration
  ack_deadline_seconds       = 20
  message_retention_duration = "86400s" # 1 day

  # Define the retry policy
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}