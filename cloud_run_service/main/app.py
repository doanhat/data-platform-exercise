import os
from datetime import datetime

from flask import Flask, request
from google.cloud import firestore
from google.cloud.firestore_v1 import Transaction, DocumentSnapshot
from dateutil.relativedelta import relativedelta
from client import FirestoreClient
from processor import Processor
from constants import TransactionStatus
from exceptions import ProcessorError
from logger import logger
from tools import calculate_card_order_fee, call_fee_service

app = Flask(__name__)


def process_card_order_transaction(
    processor: Processor,
    transaction: DocumentSnapshot,
):
    user_id = transaction.get("user_id")
    user = processor.user_collections.document(user_id).get()
    subscription_type = user.get("subscription_type")
    counter_type = "total_card_order_count"
    counter = processor.db.get_document_from_collection(
        processor.counter_collections,
        user_id,
        True,
        {counter_type: 0},
    )
    current_cards_ordered = user.to_dict().get("total_cards_ordered", 0)
    fee, calculable = calculate_card_order_fee(subscription_type, current_cards_ordered)

    logger.info(f"Transaction - {transaction.id} - User - {user_id} - Fee - {str(fee)}")
    if calculable:
        response = call_fee_service(fee, user)
        if not response:
            calculable = False
        if counter_type in counter.to_dict():
            counter.reference.update({counter_type: firestore.Increment(1)})
        else:
            if len(counter.to_dict()) > 0:
                counter.reference.update({counter_type: 1})
            else:
                counter.reference.set({counter_type: 1})
        user.reference.update({"total_cards_ordered": firestore.Increment(1)})
    transaction.reference.update(
        {
            "status": (
                TransactionStatus.COMPLETED.value
                if calculable
                else TransactionStatus.FAILED.value
            ),
            "fee": fee,
        },
    )


@app.errorhandler(ProcessorError)
def handle_processor_error(error):
    app.logger.error(f"Processor Error: {str(error)}")
    return {"status": "error", "message": str(error), "code": 500}, 500


@app.route("/monthly_fees")
def process_monthly_fees():
    try:
        args = request.args.to_dict(flat=False)
        logger.info("Begin monthly fee processing")
        logger.info(args)
        execution_date = datetime.strptime(request.args.get("date"), "%Y-%m-%d")
        end_date = datetime(execution_date.year, execution_date.month, 1)
        start_date = end_date - relativedelta(months=1)

        fs = FirestoreClient()
        processor = Processor(fs, start_date, end_date)
        card_order_transactions = processor.get_card_order_transactions()

        for transaction in card_order_transactions:
            try:
                process_card_order_transaction(processor, transaction)
            except ProcessorError as e:
                # Log the error but continue processing other transactions
                logger.error(f"Error processing transaction {transaction}: {str(e)}")
                continue

        return {
            "status": "success",
            "message": "Monthly fees processed successfully",
            "code": 200,
        }, 200

    except Exception as e:
        # This will catch any unhandled exceptions in the main block
        raise e


if __name__ == "__main__":
    app.run(
        debug=True,
        use_debugger=False,
        use_reloader=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
    )
