import pytest
from cloud_run_service.main.constants import SubscriptionType
from cloud_run_service.main.tools import calculate_card_order_fee


@pytest.mark.parametrize(
    "subscription_type, current_cards_ordered, expected_fee, expected_status",
    [
        # BASIC Subscription tests
        (SubscriptionType.BASIC.value, 0, 5, True),
        (SubscriptionType.BASIC.value, 4, 5, True),
        (SubscriptionType.BASIC.value, 5, None, False),
        # PLUS Subscription tests
        (SubscriptionType.PLUS.value, 0, 0, True),
        (SubscriptionType.PLUS.value, 9, 5, True),
        (SubscriptionType.PLUS.value, 10, None, False),
        # PRO Subscription tests
        (SubscriptionType.PRO.value, 0, 0, True),
        (SubscriptionType.PRO.value, 9, 0, True),
        (SubscriptionType.PRO.value, 10, 5, True),
        (SubscriptionType.PRO.value, 11, 5, True),
        # Invalid inputs
        ("INVALID_SUBSCRIPTION", 0, None, False),
    ],
)
def test_calculate_card_order_fee(
    subscription_type, current_cards_ordered, expected_fee, expected_status
):
    fee, status = calculate_card_order_fee(subscription_type, current_cards_ordered)
    assert fee == expected_fee
    assert status == expected_status


if __name__ == "__main__":
    pytest.main([__file__])
