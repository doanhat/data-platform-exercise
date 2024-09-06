import pytest

from functions.processor.configs import *
from functions.processor.tools import (
    add_transaction,
    update_transaction,
    check_monthly_counter_existence,
    update_failed_transaction,
    add_failed_transaction,
)


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    import firebase_admin

    firebase_admin.initialize_app()
    from local.populator.firestore_initializer import init_users

    init_users(db)

    yield

    db.recursive_delete(db.collection("transactions"))
    db.recursive_delete(db.collection("users"))
    db.recursive_delete(db.collection("counters_2024_09"))


@pytest.mark.order(1)
@pytest.mark.parametrize(
    "data, expected_transaction, expected_transaction_status",
    [
        (
            {
                "transaction_id": "1",
                "user_id": "1",
                "type": "bank_transfer",
                "amount": 1063,
                "date": "2024-09-01T00:54:50.508787Z",
            },
            True,
            "in-progress",
        ),
        (
            {
                "transaction_id": "1",
                "user_id": "1",
                "type": "bank_transfer",
                "amount": 1063,
                "date": "2024-09-01T00:54:50.508787Z",
            },
            False,  # transaction already existed,
            "in-progress",
        ),
        (
            {
                "transaction_id": "2",
                "user_id": "1",
                "type": "card_order",
                "amount": 1,
                "date": "2024-09-01T00:54:50.508787Z",
            },
            True,
            "pending",
        ),
    ],
)
def test_add_transaction(
    data, expected_transaction, expected_transaction_status
):
    mock_transaction = db.transaction()
    mock_transaction_ref = db.collection("transactions").document(
        data["transaction_id"]
    )
    result = add_transaction(
        mock_transaction, mock_transaction_ref, data
    )

    mock_transaction_status = mock_transaction_ref.get().get("status")
    assert result == expected_transaction
    assert mock_transaction_status == expected_transaction_status


@pytest.mark.order(2)
@pytest.mark.parametrize("data", [({"user_id": "2"})])
def test_check_monthly_counter_existence(data):
    from local.populator.firestore_initializer import init_transactions

    init_transactions(db)

    mock_transaction = db.transaction()
    mock_counter_ref = db.collection("counters_2024_09").document(data["user_id"])

    check_monthly_counter_existence(mock_transaction, mock_counter_ref)

    assert mock_counter_ref.get().exists


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "data, expected_cards_ordered, expected_transaction_fee, expected_transaction_status, expected_transaction_counter",
    [
        (
            {
                "transaction_id": "3",
                "user_id": "2",
                "type": "international_card_payment",
            },
            5,
            0,
            "completed",
            1,
        ),
        (
            {"transaction_id": "4", "user_id": "2", "type": "bank_transfer"},
            5,
            0,
            "completed",
            1,
        ),
        (
            {"transaction_id": "5", "user_id": "2", "type": "check_deposit"},
            5,
            0,
            "completed",
            1,
        ),
    ],
)
def test_update_transaction(
    data,
    expected_cards_ordered,
    expected_transaction_fee,
    expected_transaction_status,
    expected_transaction_counter,
):
    from local.populator.firestore_initializer import init_transactions

    init_transactions(db)

    mock_transaction = db.transaction()
    mock_transaction_ref = db.collection("transactions").document(
        data["transaction_id"]
    )
    mock_user_ref = db.collection("users").document(data["user_id"])
    mock_counter_ref = db.collection("counters_2024_09").document(data["user_id"])

    update_transaction(
        mock_transaction, mock_transaction_ref, mock_user_ref, mock_counter_ref
    )

    mock_cards_ordered = mock_user_ref.get().get("total_cards_ordered")
    mock_transaction_fee = mock_transaction_ref.get().get("fee")
    mock_transaction_status = mock_transaction_ref.get().get("status")
    mock_transaction_counter = mock_counter_ref.get().get(f"total_{data['type']}_count")

    assert mock_cards_ordered == expected_cards_ordered
    assert mock_transaction_fee == expected_transaction_fee
    assert mock_transaction_status == expected_transaction_status
    assert mock_transaction_counter == expected_transaction_counter


@pytest.mark.order(4)
@pytest.mark.parametrize(
    "data, expected_transaction_status", [({"transaction_id": "5"}, "failed")]
)
def test_update_failed_transactions(data, expected_transaction_status):
    mock_transaction = db.transaction()
    mock_transaction_ref = db.collection("transactions").document(
        data["transaction_id"]
    )

    update_failed_transaction(mock_transaction, mock_transaction_ref)
    mock_transaction_status = mock_transaction_ref.get().get("status")

    assert mock_transaction_status == expected_transaction_status


@pytest.mark.order(5)
@pytest.mark.parametrize(
    "data, expected_result, expected_transaction_status",
    [
        (
            {
                "transaction_id": "6",
                "user_id": "1",
                "type": "card_order",
                "amount": 1,
                "date": "2024-09-01T00:54:50.508787Z",
            },
            True,
            "failed",
        ),
        (
            {
                "transaction_id": "6",
                "user_id": "1",
                "type": "card_order",
                "amount": 1,
                "date": "2024-09-01T00:54:50.508787Z",
            },
            False,
            "failed",
        ),
    ],
)
def test_add_failed_transaction(data, expected_result, expected_transaction_status):
    mock_transaction = db.transaction()
    mock_transaction_ref = db.collection("transactions").document(
        data["transaction_id"]
    )

    result = add_failed_transaction(mock_transaction, mock_transaction_ref, data)
    mock_transaction_status = mock_transaction_ref.get().get("status")

    assert mock_transaction_status == expected_transaction_status
    assert result == expected_result


if __name__ == "__main__":
    pytest.main([__file__])
