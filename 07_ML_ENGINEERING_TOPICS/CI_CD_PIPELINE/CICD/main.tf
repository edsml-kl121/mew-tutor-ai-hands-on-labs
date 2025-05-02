# main.tf

# Configure the Google Cloud provider
provider "google" {
  project = "your-project-id"
  region  = "us-central1"
}

# Create a Google Cloud Storage bucket
resource "google_storage_bucket" "mew_bucket" {
  name     = "mew"
  location = "US"
}

# Upload the text.txt file to the bucket
resource "google_storage_bucket_object" "text_file" {
  name   = "text.txt"
  bucket = google_storage_bucket.mew_bucket.name
  source = "text.txt"
}