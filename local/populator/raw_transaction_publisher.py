import json
import random
from datetime import datetime
from google.cloud import pubsub_v1
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = os.getenv("TOPIC_ID")

# Initialize Pub/Sub client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# Read user data from JSON file
with open("local/populator/users.json", "r") as file:
    users = json.load(file)

# Transaction types
transaction_types = [
    "international_card_payment",
    "bank_transfer",
    "check_deposit",
    "card_order",
]


def generate_transaction(i, user_id, transaction_type):
    if transaction_type == "card_order":
        amount = 1
    else:
        amount = random.randint(1000, 10000)

    transaction = {
        "transaction_id": str(i),
        "user_id": user_id,
        "type": transaction_type,
        "amount": amount,
        "date": datetime.utcnow().isoformat()
                + "Z",  # ISO 8601 format with UTC timezone
    }

    return json.dumps(transaction)


def publish_random_messages():
    user_ids = list(range(1, len(users) + 1))  # User IDs from 1 to len(users)

    # Create a list of transactions ensuring every user gets at least one transaction
    transactions = []

    # Ensure every user has at least one transaction
    used_transaction_types = random.sample(
        transaction_types, min(len(transaction_types), len(user_ids))
    )
    for i, user_id in enumerate(user_ids):
        transaction_type = used_transaction_types[i % len(used_transaction_types)]
        transactions.append((user_id, transaction_type))

    # Ensure that all transaction types are included if there are more slots available
    remaining_transaction_types = set(transaction_types) - set(
        t for _, t in transactions
    )
    while remaining_transaction_types and len(transactions) < 10:
        user_id = random.choice(user_ids)
        transaction_type = remaining_transaction_types.pop()
        transactions.append((user_id, transaction_type))

    # Fill the remaining slots to reach a total of 10 transactions
    while len(transactions) < 10:
        user_id = random.choice(user_ids)
        transaction_type = random.choice(transaction_types)
        transactions.append((user_id, transaction_type))

    # Publish transactions
    for i, (user_id, transaction_type) in enumerate(transactions):
        transaction = generate_transaction(i, user_id, transaction_type)

        future = publisher.publish(topic_path, transaction.encode("utf-8"))
        print(f"Published message ID: {future.result()}")


def publish_sample_transactions(path="local/populator/raw_transactions.json"):
    with open(path, "r") as file:
        transactions = json.load(file)
        for transaction in transactions:
            future = publisher.publish(
                topic_path, json.dumps(transaction).encode("utf-8")
            )
            print(f"Published message ID: {future.result()}")


if __name__ == "__main__":
    publish_sample_transactions()
