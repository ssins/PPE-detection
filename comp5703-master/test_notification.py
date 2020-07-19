from unittest import TestCase

from notification import NotificationService


class TestNotificationService(TestCase):
    def test_notify(self):
        username = 'ppe.detection@gmail.com'
        password = 'itsdxkjynqhwsgaj'
        host = 'smtp.gmail.com'
        port = 587

        noti = NotificationService(host, port, username, password, False)
        noti.notify(0, 'guneedmts@gmail.com', 'Unit Test')

