from django.test import TestCase
from unittest.mock import patch
from notifications.tasks import send_transaction_notification

class NotificationTaskTests(TestCase):
    @patch('notifications.tasks.send_transaction_notification.delay')
    def test_notification_task_called(self, mock_task):
        mock_task('test@test.com', 'deposit', '1000.00')
        mock_task.assert_called_once_with('test@test.com', 'deposit', '1000.00')