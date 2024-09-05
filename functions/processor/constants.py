from enum import Enum


class SubscriptionType(Enum):
    BASIC = "Basic"
    PLUS = "Plus"
    PRO = "Pro"


class TransactionType(Enum):
    INT_CARD_PAYMENT = "international_card_payment"
    BANK_TRANSFER = "bank_transfer"
    CHECK_DEPOSIT = "check_deposit"
    CARD_ORDER = "card_order"


class TransactionStatus(Enum):
    IN_PROGRESS = "in-progress"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
