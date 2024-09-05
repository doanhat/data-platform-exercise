import os

from google.cloud import pubsub_v1, firestore, firestore_admin_v1, logging

logger = logging.Client()
logger.setup_logging()
db = firestore.Client()
fb_transaction = db.transaction()  # Firebase transaction for atomic operations
publisher = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(
    os.getenv("PROJECT_ID"), os.getenv("TOPIC_NAME", None)
)
DLQ_PATH = publisher.topic_path(os.getenv("PROJECT_ID"), os.getenv("DLQ_NAME"))
EVENT_MAX_AGE = int(os.getenv("EVENT_MAX_AGE"))
client = firestore_admin_v1.FirestoreAdminClient()
