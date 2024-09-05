import json
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def init_users(db=None, path="local/populator/users.json"):
    with open(path, "r") as file:
        users = json.load(file)

    for i, user in enumerate(users):
        doc_ref = db.collection("users").document(str(i + 1))
        doc_ref.set(user)

    print("Users added to Firestore successfully.")


def init_transactions(db=None, path="local/populator/test_2_raw_transactions.json"):
    with open(path, "r") as file:
        transactions = json.load(file)

    for i, transaction in enumerate(transactions):
        doc_ref = db.collection("transactions").document(transaction["transaction_id"])
        transaction["date"] = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
        doc_ref.set(transaction)

    print("Transactions added to Firestore successfully.")


def init_counters(db=None, path="local/populator/dataflow_counters.json"):
    with open(path, "r") as file:
        counters = json.load(file)
    for i, counter in enumerate(counters):
        doc_ref = db.collection("counters_2024_09").document(str(i + 1))
        doc_ref.set(counter)

    print("Counters added to Firestore successfully.")


if __name__ == "__main__":
    # Use the application default credentials.
    cred = credentials.ApplicationDefault()

    firebase_admin.initialize_app(cred)
    db = firestore.client()
    init_users(db)
    init_transactions(db)
    print("ok")
