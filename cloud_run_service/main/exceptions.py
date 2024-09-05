class ProcessorError(Exception):
    pass


class FirestoreError(Exception):
    pass


class DocumentNotFoundError(FirestoreError):
    pass


class FirestoreTransactionError(FirestoreError):
    pass
