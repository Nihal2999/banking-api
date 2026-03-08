from rest_framework import serializers
from .models import Transaction
from accounts.models import BankAccount


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id", "user", "from_account", "to_account",
            "transaction_type", "amount", "status",
            "description", "created_at"
        ]
        read_only_fields = ["id", "user", "status", "created_at"]


class DepositSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class WithdrawalSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class TransferSerializer(serializers.Serializer):
    from_account_id = serializers.UUIDField()
    to_account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate(self, attrs):
        if attrs["from_account_id"] == attrs["to_account_id"]:
            raise serializers.ValidationError("Cannot transfer to same account")
        return attrs