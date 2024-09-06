import functions_framework, logging
from cloudevents.http import CloudEvent
from configs import DLQ_PATH, fb_transaction, db, TOPIC_PATH
from constants import TransactionStatus
from tools import (
    add_transaction,
    update_failed_transaction,
    update_transaction,
    add_failed_transaction,
    extract_data,
    is_old,
    publish_message,
    check_status,
    get_date_from_str,
    check_monthly_counter_existence,
)


@functions_framework.cloud_event
def preprocess(event: CloudEvent):
    data = extract_data(event)
    transaction_ref = db.collection("transactions").document(data["transaction_id"])

    if is_old(event):
        add_failed_transaction(fb_transaction, transaction_ref, data)
        publish_message(DLQ_PATH, data)
        logging.info("Transaction processing failed, move to DLQ.")
        return 201

    response = add_transaction(fb_transaction, transaction_ref, data)
    if not response:
        logging.info("Transaction already exists.")
        return 201

    publish_message(TOPIC_PATH, data)
    logging.info("Transaction received and processing started.")
    return 201


@functions_framework.cloud_event
def process_fee(event: CloudEvent):
    data = extract_data(event)
    transaction_ref = db.collection("transactions").document(data["transaction_id"])
    user_ref = db.collection("users").document(data["user_id"])
    counter_ref = db.collection(f"counters_{get_date_from_str(event)}").document(
        data["user_id"]
    )
    if is_old(event):
        update_failed_transaction(fb_transaction, transaction_ref)
        publish_message(DLQ_PATH, data)
        logging.info("Fee processing failed, move to DLQ.")
        return 201

    if check_status(transaction_ref, TransactionStatus.COMPLETED.value):
        logging.info("Fee has been already applied.")
        return 201

    if not check_status(transaction_ref, TransactionStatus.IN_PROGRESS.value):
        logging.info("Not an in-progress transaction, ignore.")
        return 201

    check_monthly_counter_existence(fb_transaction, counter_ref)
    update_transaction(fb_transaction, transaction_ref, user_ref, counter_ref)

    logging.info("Fee has been successfully applied.")
    return 201
