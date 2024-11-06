locals {
  project_id      = "data-platform-exercise"
  gcp_region      = "europe-west1"

  bucket_name = "billing-bucket-885070032799"

  raw_transaction_topic_name = "raw-transaction-topic"
  raw_transaction_dlq_name = "raw-transaction-dlq"
  raw_transaction_subscription_name = "raw-transaction-subscription"
  in_progress_transaction_topic_name = "in-progress-transaction-topic"
  in_progress_transaction_dlq_name = "in-progress-transaction-dlq"
  in_progress_transaction_subscription_name = "in-progress-transaction-subscription"
  event_max_age = 60 # in seconds

  preprocessing_function_name = "raw-transaction-preprocessor"
  preprocessing_function_entrypoint = "preprocess"
  fee_processing_function_name = "fee-processor"
  fee_processing_function_entrypoint = "process_fee"
  source_code_object_name = "processor/${lower(replace(base64encode(data.archive_file.processor_zip.output_md5), "=", ""))}.zip"

  monthly_fee_processing_service_name = "monthly-fee-processor"
  monthly_fee_processing_service_repo = "monthly-fee-processor-repo"

  workflow_name = "monthly-workflow"
  dataflow_job_name = "billing-processing-flow"

  scheduler_name = "monthly-scheduler"
  scheduler_cron = "0 0 1 * *" # First day of each month
  scheduler_tz = "Etc/UTC"
  scheduler_attempt = "300s"
}