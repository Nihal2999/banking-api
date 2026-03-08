from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from accounts.models import BankAccount
from .models import Transaction
from .serializers import (
    TransactionSerializer,
    DepositSerializer,
    WithdrawalSerializer,
    TransferSerializer,
)
from notifications.tasks import send_transaction_notification


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_id = serializer.validated_data["account_id"]
        amount = serializer.validated_data["amount"]
        description = serializer.validated_data.get("description", "")

        try:
            account = BankAccount.objects.select_for_update().get(
                id=account_id, user=request.user, status="active"
            )
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        account.balance += amount
        account.save()

        txn = Transaction.objects.create(
            user=request.user,
            to_account=account,
            transaction_type="deposit",
            amount=amount,
            status="completed",
            description=description,
        )

        # Celery task
        send_transaction_notification.delay(
            str(request.user.id), "deposit", str(amount)
        )

        return Response({
            "message": "Deposit successful",
            "transaction": TransactionSerializer(txn).data,
            "new_balance": str(account.balance),
        }, status=status.HTTP_201_CREATED)


class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_id = serializer.validated_data["account_id"]
        amount = serializer.validated_data["amount"]
        description = serializer.validated_data.get("description", "")

        try:
            account = BankAccount.objects.select_for_update().get(
                id=account_id, user=request.user, status="active"
            )
        except BankAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        if account.balance < amount:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        account.balance -= amount
        account.save()

        txn = Transaction.objects.create(
            user=request.user,
            from_account=account,
            transaction_type="withdrawal",
            amount=amount,
            status="completed",
            description=description,
        )

        send_transaction_notification.delay(
            str(request.user.id), "withdrawal", str(amount)
        )

        return Response({
            "message": "Withdrawal successful",
            "transaction": TransactionSerializer(txn).data,
            "new_balance": str(account.balance),
        }, status=status.HTTP_201_CREATED)


class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_account_id = serializer.validated_data["from_account_id"]
        to_account_id = serializer.validated_data["to_account_id"]
        amount = serializer.validated_data["amount"]
        description = serializer.validated_data.get("description", "")

        try:
            from_account = BankAccount.objects.select_for_update().get(
                id=from_account_id, user=request.user, status="active"
            )
        except BankAccount.DoesNotExist:
            return Response({"error": "Source account not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            to_account = BankAccount.objects.select_for_update().get(
                id=to_account_id, status="active"
            )
        except BankAccount.DoesNotExist:
            return Response({"error": "Destination account not found"}, status=status.HTTP_404_NOT_FOUND)

        if from_account.balance < amount:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()

        txn = Transaction.objects.create(
            user=request.user,
            from_account=from_account,
            to_account=to_account,
            transaction_type="transfer",
            amount=amount,
            status="completed",
            description=description,
        )

        send_transaction_notification.delay(
            str(request.user.id), "transfer", str(amount)
        )

        return Response({
            "message": "Transfer successful",
            "transaction": TransactionSerializer(txn).data,
        }, status=status.HTTP_201_CREATED)


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)