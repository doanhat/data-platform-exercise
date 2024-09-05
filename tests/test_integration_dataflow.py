import json

import pytest

from dataflow.custom.io_operations import gcs_client
from dataflow.pipeline import run


@pytest.fixture(scope="session")
def bucket(pytestconfig):
    return pytestconfig.getoption("bucket")


@pytest.fixture(scope="session")
def date(pytestconfig):
    return pytestconfig.getoption("date")


@pytest.fixture(scope="session")
def runner(pytestconfig):
    return pytestconfig.getoption("runner")


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    from local.populator.firestore_initializer import (
        init_counters,
        init_users,
        init_transactions,
    )
    from dataflow.custom.io_operations import db

    # Init Firestore
    init_users(db, "local/populator/dataflow_users.json")
    init_transactions(db, "local/populator/dataflow_transactions.json")
    init_counters(db, "local/populator/dataflow_counters.json")

    # Init GCS
    mock_bucket = gcs_client.create_bucket("test-bucket")
    blob = mock_bucket.blob("2024/09/1.json")
    blob.upload_from_string("test1")

    yield

    gcs_client.bucket("test-bucket").delete(force=True)
    db.recursive_delete(db.collection("transactions"))
    db.recursive_delete(db.collection("users"))
    db.recursive_delete(db.collection("counters_2024_09"))


def test_pipeline(bucket, date):
    # Run Beam flow
    run()
    results = []
    for blob in gcs_client.get_bucket("test-bucket").list_blobs():
        content = blob.download_as_bytes()
        data = json.loads(content)
        print("---")
        print(data)
        results.append(data)
    expected_results = [
        {
            "name": "Bob",
            "subscription_type": "Plus",
            "total_card_order_count": 6,
            "total_cards_ordered": 7,
            "total_check_deposit_count": 1,
            "total_fee": 5,
        },
        {
            "name": "Alice",
            "subscription_type": "Basic",
            "total_bank_transfer_count": 1,
            "total_card_order_count": 1,
            "total_cards_ordered": 2,
            "total_fee": 5,
        },
        {
            "name": "Charlie",
            "subscription_type": "Pro",
            "total_card_order_count": 11,
            "total_cards_ordered": 15,
            "total_fee": 5,
            "total_international_card_payment_count": 1,
        },
    ]

    assert sorted(expected_results, key=lambda x: sorted(x.items())) == sorted(
        results, key=lambda x: sorted(x.items())
    )


if __name__ == "__main__":
    pytest.main([__file__])
