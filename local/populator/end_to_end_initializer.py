import json
import random
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import pubsub_v1
from faker import Faker

fake = Faker()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("shine-assignment",
                                  "raw-transaction-topic")
cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred)
db = firestore.client()


def init_users(path="users.json"):
    with open(path, "r") as file:
        users = json.load(file)

    for i, user in enumerate(users):
        doc_ref = db.collection("users").document(str(i + 1))
        doc_ref.set(user)

    print("Users added to Firestore successfully.")
    return users


def init_transactions(users):
    user_ids = list(range(1, len(users) + 1))  # User IDs from 1 to len(users)
    user_counter = {}
    for i, user in enumerate(users):
        user_counter[str(i + 1)] = user
    # Create a list of transactions ensuring every user gets at least one transaction

    transaction_types = [
        "international_card_payment",
        "bank_transfer",
        "check_deposit",
        "card_order",
    ]

    def generate_transaction(i):
        user_id = random.choice(user_ids)
        transaction_type = random.choice(transaction_types)
        amount = random.choice(range(10000)) if transaction_type != 'card_order' else 1
        transaction_date = fake.date_time_between_dates(
            datetime(2024, 8, 1),
            datetime(2024, 11, 1),
        ).isoformat() + "Z"
        return {
            "transaction_id": str(i+1),
            "user_id": str(user_id),
            "type": transaction_type,
            "amount": amount,
            "date": transaction_date
        }

    for i in range(100000):
        need_another = True
        tx = {}
        while need_another:
            tx = generate_transaction(i)
            tx_type = tx["type"]
            if tx_type == 'card_order':
                cards_ordered = user_counter[tx["user_id"]]["total_cards_ordered"]
                subscription_type = user_counter[tx["user_id"]]["subscription_type"]

                if subscription_type == "Basic":
                    if cards_ordered < 5:
                        need_another = False
                        user_counter[tx["user_id"]]["total_cards_ordered"] = user_counter[tx["user_id"]]["total_cards_ordered"] + 1
                    else:
                        need_another = True
                elif subscription_type == "Plus":
                    if cards_ordered < 10:
                        need_another = False
                        user_counter[tx["user_id"]]["total_cards_ordered"] = user_counter[tx["user_id"]]["total_cards_ordered"] + 1
                    else:
                        need_another = True
                else:
                    need_another = False
                    user_counter[tx["user_id"]]["total_cards_ordered"] = user_counter[tx["user_id"]]["total_cards_ordered"] + 1
            else:
                need_another = False

        future = publisher.publish(topic_path, json.dumps(tx).encode("utf-8"))
        print(f"Published message ID: {future.result()}")


if __name__ == "__main__":
    users = init_users()
    init_transactions(users)
    print("ok")
