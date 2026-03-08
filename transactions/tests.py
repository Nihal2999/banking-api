from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import BankAccount
from unittest.mock import patch

User = get_user_model()

class TransactionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='Test@1234'
        )
        self.account = BankAccount.objects.create(
            user=self.user,
            account_type='savings',
            account_number='BANK000000001'
        )
        # Login and set token
        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': 'Test@1234'
        })
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access_token']}"
        )

    @patch('notifications.tasks.send_transaction_notification.delay')
    def test_deposit(self, mock_task):
        response = self.client.post('/api/transactions/deposit/', {
            'account_id': str(self.account.id),
            'amount': '1000.00',
            'description': 'Test deposit'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['new_balance'], '1000.00')
        mock_task.assert_called_once()

    @patch('notifications.tasks.send_transaction_notification.delay')
    def test_withdrawal(self, mock_task):
        self.account.balance = 2000
        self.account.save()
        response = self.client.post('/api/transactions/withdraw/', {
            'account_id': str(self.account.id),
            'amount': '500.00',
            'description': 'Test withdrawal'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['new_balance'], '1500.00')

    @patch('notifications.tasks.send_transaction_notification.delay')
    def test_insufficient_funds(self, mock_task):
        response = self.client.post('/api/transactions/withdraw/', {
            'account_id': str(self.account.id),
            'amount': '9999.00',
            'description': 'Test'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('notifications.tasks.send_transaction_notification.delay')
    def test_transfer(self, mock_task):
        self.account.balance = 2000
        self.account.save()
        account2 = BankAccount.objects.create(
            user=self.user,
            account_type='current',
            account_number='BANK000000002'
        )
        response = self.client.post('/api/transactions/transfer/', {
            'from_account_id': str(self.account.id),
            'to_account_id': str(account2.id),
            'amount': '500.00',
            'description': 'Test transfer'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)