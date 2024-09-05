resource "google_storage_bucket" "transaction_bucket" {
  location = local.gcp_region
  name     = local.bucket_name
}
# Code
data "archive_file" "processor_zip" {
  type        = "zip"
  output_path = "/tmp/cloud_function.zip"
  source_dir  = "../../functions/processor/"
}
resource "google_storage_bucket_object" "processor_code" {
  name   = local.source_code_object_name
  bucket = google_storage_bucket.transaction_bucket.name
  source = data.archive_file.processor_zip.output_path
}