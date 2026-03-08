from django.urls import path
from .views import (
    DepositView,
    WithdrawalView,
    TransferView,
    TransactionHistoryView,
    TransactionDetailView,
)

urlpatterns = [
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("withdraw/", WithdrawalView.as_view(), name="withdraw"),
    path("transfer/", TransferView.as_view(), name="transfer"),
    path("history/", TransactionHistoryView.as_view(), name="transaction-history"),
    path("<uuid:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
]