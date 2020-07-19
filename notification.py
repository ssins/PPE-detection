import asyncio
import smtplib


class NotificationService:
    username = ''
    password = ''
    host = ''
    port = ''
    ssl = False

    def __init__(self, host, port, username, password, ssl):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.ssl = ssl

    def count(self, mode):
        self.counter[mode] += 1

    def reset_count(self, mode):
        self.counter[mode] = 0

    async def notify(self, notification_type, receiver, message):
        if notification_type == 0:
            with smtplib.SMTP(self.host, self.port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(self.username, self.password)

                subject = 'Eyre Notification'

                mail = 'Subject: {}\n\n{}'.format(subject, message)

                smtp.sendmail(self.username, receiver, mail)
