from django.db import models
from accounts.models import BankAccount, User
import uuid


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    from_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE,
        related_name="sent_transactions", null=True, blank=True
    )
    to_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE,
        related_name="received_transactions", null=True, blank=True
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.status}"

    class Meta:
        ordering = ["-created_at"]