from datetime import datetime

from google.cloud.firestore_v1 import (
    CollectionReference,
    Query,
    FieldFilter,
    DocumentSnapshot,
)

from google.cloud.firestore_v1.stream_generator import StreamGenerator
from constants import TransactionStatus, TransactionType

from client import FirestoreClient


class Processor:
    def __init__(self, db: FirestoreClient, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_str = datetime.strftime(self.start_date, "%Y_%m")
        self.db = db

        self.counter_collections = self.init_collections(
            f"counters_{self.start_date_str}"
        )
        self.user_collections = self.init_collections("users")
        self.transaction_collections = self.init_collections("transactions")

    def init_collections(self, collection_name: str) -> CollectionReference:
        return self.db.get_collection(collection_name)

    def get_transaction_query(self) -> Query:
        return self.transaction_collections.where(
            filter=FieldFilter("date", ">=", self.start_date)
        ).where(filter=FieldFilter("date", "<", self.end_date))

    def get_card_order_transactions(self) -> StreamGenerator[DocumentSnapshot]:
        return (
            self.get_transaction_query()
            .where(filter=FieldFilter("type", "==", TransactionType.CARD_ORDER.value))
            .where(filter=FieldFilter("status", "==", TransactionStatus.PENDING.value))
            .stream()
        )

    def get_completed_transactions(self) -> StreamGenerator[DocumentSnapshot]:
        return (
            self.get_transaction_query()
            .where(
                filter=FieldFilter("status", "==", TransactionStatus.COMPLETED.value)
            )
            .stream()
        )
