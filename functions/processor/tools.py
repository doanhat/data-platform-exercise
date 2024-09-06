import base64
import json
from datetime import datetime, timezone

from cloudevents.http import CloudEvent
from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentReference, Transaction, DocumentSnapshot

from configs import EVENT_MAX_AGE, publisher
from constants import TransactionType, SubscriptionType


@firestore.transactional
def add_transaction(
    firebase_transaction: Transaction,
    transaction_ref: DocumentReference,
    data: dict,
) -> bool:
    transaction_snapshot = transaction_ref.get(transaction=firebase_transaction)
    if transaction_snapshot.exists:
        return False

    data_structure = {
        "user_id": data["user_id"],
        "type": data["type"],
        "amount": data["amount"],
        "date": datetime.fromisoformat(data["date"].replace("Z", "+00:00")),
        "fee": None,
        "status": "in-progress" if data["type"] != "card_order" else "pending",
    }
    firebase_transaction.set(transaction_ref, data_structure)
    return True


@firestore.transactional
def update_transaction(
    firebase_transaction: Transaction,
    transaction_ref: DocumentReference,
    user_ref: DocumentReference,
    counter_ref: DocumentReference,
):
    transaction_snapshot = get_firestore_snapshot(transaction_ref, firebase_transaction)
    user_snapshot = get_firestore_snapshot(user_ref, firebase_transaction)
    counter_snapshot = get_firestore_snapshot(counter_ref, firebase_transaction)
    counter_snapshot_dict = counter_snapshot.to_dict()
    transaction_type = transaction_snapshot.get("type")
    counter_type = f"total_{transaction_type}_count"
    subscription_type = user_snapshot.get("subscription_type")

    if counter_type in counter_snapshot.to_dict():
        current_count = counter_snapshot.get(counter_type)
        fee = calculate_fee(transaction_type, subscription_type, current_count)
        call_fee_service(fee, user_snapshot)
        firebase_transaction.update(counter_ref, {counter_type: firestore.Increment(1)})
    else:
        current_count = 0
        fee = calculate_fee(transaction_type, subscription_type, current_count)
        call_fee_service(fee, user_snapshot)
        if len(counter_snapshot_dict):
            firebase_transaction.update(counter_ref, {counter_type: 1})
        else:
            firebase_transaction.set(counter_ref, {counter_type: 1})

    firebase_transaction.update(transaction_ref, {"fee": fee, "status": "completed"})


@firestore.transactional
def check_monthly_counter_existence(
    firebase_transaction: Transaction, counter_ref: DocumentReference
):
    get_firestore_snapshot(counter_ref, firebase_transaction, True)


@firestore.transactional
def update_failed_transaction(
    firebase_transaction: Transaction, transaction_ref: DocumentReference
):
    transaction_snapshot = transaction_ref.get(transaction=firebase_transaction)
    if not transaction_snapshot.exists:
        raise Exception("Transaction does not exist.")

    firebase_transaction.update(transaction_ref, {"status": "failed"})


@firestore.transactional
def add_failed_transaction(
    firebase_transaction: Transaction, transaction_ref: DocumentReference, data: dict
):
    transaction_snapshot = transaction_ref.get(transaction=firebase_transaction)
    if transaction_snapshot.exists:
        return False

    data_structure = {
        "user_id": data["user_id"],
        "type": data["type"],
        "amount": data["amount"],
        "date": datetime.fromisoformat(data["date"].replace("Z", "+00:00")),
        "fee": None,
        "status": "failed",
    }
    firebase_transaction.set(transaction_ref, data_structure)
    return True


def calculate_fee(
    transaction_type: str, subscription_type: str, current_count: int
) -> int:
    fee = None
    if transaction_type == TransactionType.INT_CARD_PAYMENT.value:
        if subscription_type == SubscriptionType.BASIC.value:
            fee = 5
        if subscription_type == SubscriptionType.PLUS.value:
            fee = 0 if current_count < 5 else 5
        if subscription_type == SubscriptionType.PRO.value:
            fee = 0

    if transaction_type == TransactionType.BANK_TRANSFER.value:
        if subscription_type == SubscriptionType.BASIC.value:
            fee = 0 if current_count < 10 else 2
        if subscription_type == SubscriptionType.PLUS.value:
            fee = 0 if current_count < 15 else 2
        if subscription_type == SubscriptionType.PRO.value:
            fee = 0 if current_count < 30 else 2

    if transaction_type == TransactionType.CHECK_DEPOSIT.value:
        if subscription_type == SubscriptionType.BASIC.value:
            fee = 2
        if subscription_type == SubscriptionType.PLUS.value:
            fee = 0 if current_count < 5 else 2
        if subscription_type == SubscriptionType.PRO.value:
            fee = 0
    return fee


def call_fee_service(amount, user) -> bool:
    print(amount, user)
    return True


def extract_data(event: CloudEvent):
    return json.loads(base64.b64decode(event.data["message"]["data"]).decode())


def is_old(event: CloudEvent) -> bool:
    return (
        datetime.now(timezone.utc)
        - datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
    ).total_seconds() > EVENT_MAX_AGE


def check_status(transaction_ref, status) -> bool:
    return transaction_ref.get().get("status") == status


def get_date_from_str(event: CloudEvent) -> str:
    date = datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
    return date.strftime("%Y_%m")


def publish_message(topic, data):
    future = publisher.publish(topic, data=json.dumps(data).encode("utf-8"))
    future.result()  # Blocked until the message is published


def get_firestore_snapshot(
    doc_ref: DocumentReference, firebase_transaction: Transaction, creation=False
) -> DocumentSnapshot:
    snapshot = doc_ref.get(transaction=firebase_transaction)
    if not snapshot.exists:
        if not creation:
            raise Exception(f"Document {doc_ref.id} does not exist.")
        else:
            firebase_transaction.set(doc_ref, {})
    return snapshot
