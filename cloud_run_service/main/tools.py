from typing import Tuple, Union, Optional

from constants import SubscriptionType


def calculate_card_order_fee(
    subscription_type: str, current_cards_ordered: int
) -> Union[Tuple[None, bool], Tuple[Optional[int], bool]]:
    if subscription_type == SubscriptionType.BASIC.value:
        return (5, True) if current_cards_ordered < 5 else (None, False)

    if subscription_type == SubscriptionType.PLUS.value:
        if current_cards_ordered < 5:
            return 0, True
        elif current_cards_ordered < 10:
            return 5, True
        else:
            return None, False

    if subscription_type == SubscriptionType.PRO.value:
        return (0, True) if current_cards_ordered < 10 else (5, True)

    return None, False


def call_fee_service(amount, user) -> bool:
    print(amount, user)
    return True
