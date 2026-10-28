"""
Core data models for the Bank Transaction Processing System.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"


class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNDONE = "UNDONE"


@dataclass
class Account:
    """Represents a bank customer account."""
    account_number: str
    holder_name: str
    balance: float
    created_at: datetime = datetime.now()

    def __post_init__(self):
        self.account_number = str(self.account_number).strip()
        self.holder_name = str(self.holder_name).strip()
        self.balance = round(float(self.balance), 2)

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "holder_name": self.holder_name,
            "balance": self.balance,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


@dataclass
class Transaction:
    """Represents a banking transaction."""
    tx_id: str
    tx_type: TransactionType
    from_account: str
    to_account: Optional[str]
    amount: float
    timestamp: datetime
    priority_due_time: Optional[datetime] = None
    status: TransactionStatus = TransactionStatus.PENDING
    failure_reason: Optional[str] = None
    description: str = ""

    def __post_init__(self):
        self.amount = round(float(self.amount), 2)
        if self.priority_due_time is None:
            self.priority_due_time = self.timestamp

    def to_dict(self):
        return {
            "tx_id": self.tx_id,
            "type": self.tx_type.value,
            "from_account": self.from_account,
            "to_account": self.to_account or "-",
            "amount": self.amount,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "due_time": self.priority_due_time.strftime("%Y-%m-%d %H:%M:%S") if self.priority_due_time else "-",
            "status": self.status.value,
            "failure_reason": self.failure_reason or "-",
            "description": self.description
        }
