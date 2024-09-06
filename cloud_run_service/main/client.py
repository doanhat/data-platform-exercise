from google.cloud import firestore
from google.cloud.firestore_v1 import (
    DocumentReference,
    Transaction,
    DocumentSnapshot,
    CollectionReference,
)

from exceptions import DocumentNotFoundError, FirestoreError
from logger import logger


class FirestoreClient:
    def __init__(self):
        self.db = firestore.Client()

    def get_collection(self, collection_name: str) -> CollectionReference:
        return self.db.collection(collection_name)

    def get_document(
        self,
        collection_name: str,
        document_id: str,
        creation=False,
        payload: dict = None,
    ) -> DocumentSnapshot:
        return self.get_firestore_snapshot(
            self.db.collection(collection_name).document(document_id),
            creation,
            payload,
        )

    def get_document_from_collection(
        self,
        collection: CollectionReference,
        document_id: str,
        creation=False,
        payload: dict = None,
    ) -> DocumentSnapshot:
        return self.get_firestore_snapshot(
            collection.document(document_id), creation, payload
        )

    @staticmethod
    def get_firestore_snapshot(
        doc_ref: DocumentReference,
        creation=False,
        payload: dict = None,
    ) -> DocumentSnapshot:
        try:
            snapshot = doc_ref.get()
            if not snapshot.exists:
                if not creation:
                    raise DocumentNotFoundError(
                        f"Document {doc_ref.id} does not exist."
                    )
                else:
                    doc_ref.set(payload)
                    return doc_ref.get()
            return snapshot
        except Exception as e:
            logger.error(f"Error retrieving document {doc_ref.id}: {str(e)}")
            raise FirestoreError(f"Firestore operation failed: {str(e)}") from e
