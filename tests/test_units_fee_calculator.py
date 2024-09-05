import os

import pytest

from functions.processor.constants import TransactionType, SubscriptionType
from functions.processor.tools import calculate_fee


@pytest.mark.parametrize(
    "transaction_type, subscription_type, current_count, expected_fee",
    [
        # INT_CARD_PAYMENT tests
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.BASIC.value, 0, 5),
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.BASIC.value, 10, 5),
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.PLUS.value, 4, 0),
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.PLUS.value, 5, 5),
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.PLUS.value, 10, 5),
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.PRO.value, 0, 0),
        (TransactionType.INT_CARD_PAYMENT.value, SubscriptionType.PRO.value, 100, 0),
        # BANK_TRANSFER tests
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.BASIC.value, 9, 0),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.BASIC.value, 10, 2),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.BASIC.value, 20, 2),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.PLUS.value, 14, 0),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.PLUS.value, 15, 2),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.PLUS.value, 20, 2),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.PRO.value, 29, 0),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.PRO.value, 30, 2),
        (TransactionType.BANK_TRANSFER.value, SubscriptionType.PRO.value, 40, 2),
        # CHECK_DEPOSIT tests
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.BASIC.value, 0, 2),
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.BASIC.value, 10, 2),
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.PLUS.value, 4, 0),
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.PLUS.value, 5, 2),
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.PLUS.value, 10, 2),
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.PRO.value, 0, 0),
        (TransactionType.CHECK_DEPOSIT.value, SubscriptionType.PRO.value, 100, 0),
        # Invalid inputs
        ("INVALID_TYPE", SubscriptionType.BASIC.value, 0, None),
        (TransactionType.INT_CARD_PAYMENT.value, "INVALID_SUBSCRIPTION", 0, None),
    ],
)
def test_calculate_fee(
    transaction_type, subscription_type, current_count, expected_fee
):
    assert (
        calculate_fee(transaction_type, subscription_type, current_count)
        == expected_fee
    )


if __name__ == "__main__":
    pytest.main([__file__])
