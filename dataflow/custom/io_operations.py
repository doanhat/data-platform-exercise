import json

import apache_beam as beam
from apache_beam import DoFn, ParDo
from google.cloud import storage, firestore

# Initialize Firebase
db = firestore.Client()
gcs_client = storage.Client()


# Custom PTransform to read data from Firestore
class ReadFromFirestore(beam.PTransform):
    def __init__(self, collection_name, filters=None):
        super(ReadFromFirestore, self).__init__()
        self.collection_name = collection_name
        self.filters = filters or []

    def expand(self, pcoll):
        return pcoll | "ReadFromFirestore" >> ParDo(
            ReadFirestoreFn(self.collection_name, self.filters)
        )


class ReadFirestoreFn(DoFn):
    def __init__(self, collection_name, filters):
        super(ReadFirestoreFn, self).__init__()
        self.collection_name = collection_name
        self.filters = filters

    def process(self, element):
        query = db.collection(self.collection_name)
        for field, op, value in self.filters:
            query = query.where(field, op, value)
        docs = query.stream()
        for doc in docs:
            yield doc.id, doc.to_dict()  # Include document ID (keyed by the document ID)


class ProcessTransaction(DoFn):
    def process(self, transaction):
        transaction_id, data = transaction
        user_id = data.get("user_id")
        fee = data.get("fee", 0) or 0  # Handle null fees
        yield user_id, fee


class WriteUserFileFn(DoFn):
    def __init__(self, bucket_name, prefix):
        super(WriteUserFileFn, self).__init__()
        self.bucket = None
        self.prefix = prefix
        self.bucket_name = bucket_name

    def setup(self):
        self.bucket = gcs_client.get_bucket(self.bucket_name)

    def process(self, element):
        user_id, result = element
        content = json.dumps(result)

        file_name = f"{user_id}.json"
        blob = self.bucket.blob(self.prefix + file_name)
        blob.upload_from_string(content)

        yield f"Wrote data for user_id {user_id} to {file_name}"


class DeleteGCSFolderFn(DoFn):
    def __init__(self, bucket_name, prefix, batch_size=1000):
        super(DeleteGCSFolderFn, self).__init__()
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.batch_size = batch_size

    def process(self, element):
        bucket = gcs_client.get_bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=self.prefix)

        batch = []
        if blobs:
            for blob in blobs:
                batch.append(blob)
                if len(batch) >= self.batch_size:
                    bucket.delete_blobs(batch)
                    yield f"Deleted {len(batch)} blobs"
                    batch = []  # Reset the batch

        # Delete any remaining blobs in the last batch
        if batch:
            bucket.delete_blobs(batch)
            yield f"Deleted {len(batch)} blobs"
