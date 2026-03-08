from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_transaction_notification(self, user_id, transaction_type, amount):
    try:
        user = User.objects.get(id=user_id)
        # In production this would send email/SMS
        # For now we log it
        print(f"[NOTIFICATION] User: {user.email}")
        print(f"[NOTIFICATION] Transaction: {transaction_type.upper()} of ₹{amount}")
        print(f"[NOTIFICATION] Status: Completed")
        return {
            "status": "sent",
            "user": user.email,
            "transaction_type": transaction_type,
            "amount": amount,
        }
    except User.DoesNotExist:
        print(f"[NOTIFICATION] User {user_id} not found")
        return {"status": "failed", "reason": "User not found"}
    except Exception as exc:
        print(f"[NOTIFICATION] Error: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def flag_suspicious_transaction(user_id, amount):
    try:
        user = User.objects.get(id=user_id)
        print(f"[ALERT] Suspicious transaction detected!")
        print(f"[ALERT] User: {user.email}, Amount: ₹{amount}")
        return {"status": "flagged", "user": user.email, "amount": amount}
    except User.DoesNotExist:
        return {"status": "failed"}


@shared_task
def generate_monthly_statement(user_id):
    try:
        from transactions.models import Transaction
        from django.utils import timezone
        from datetime import timedelta

        user = User.objects.get(id=user_id)
        last_month = timezone.now() - timedelta(days=30)
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=last_month
        )
        print(f"[STATEMENT] Generating statement for {user.email}")
        print(f"[STATEMENT] Total transactions: {transactions.count()}")
        return {
            "status": "generated",
            "user": user.email,
            "transaction_count": transactions.count()
        }
    except User.DoesNotExist:
        return {"status": "failed"}