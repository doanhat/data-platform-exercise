resource "google_firestore_database" "datastore_billing_database" {
  name        = local.firestore_db_name
  location_id = local.gcp_region
  type        = "FIRESTORE_NATIVE"
}

resource "google_firestore_index" "transactions_index" {
  database   = google_firestore_database.datastore_billing_database.name
  collection = "transactions"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "date"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "card_order_transactions_index" {
  database   = google_firestore_database.datastore_billing_database.name
  collection = "transactions"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }

  fields {
    field_path = "type"
    order      = "ASCENDING"
  }

  fields {
    field_path = "date"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}