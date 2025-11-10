# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
# import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import (
    SENDGRID_API_KEY,
)

emailText = "Email message from twilio SendGrid !!!"

message = Mail(
    from_email='umang.malhotra@webisdom.com',   # your verified sender,
    to_emails='UmangMalhotra1980@gmail.com',    # sample receiver
    subject='Email message from twilio SendGrid',
    html_content=emailText) #'<strong>and easy to do anywhere, even with Python</strong>')
try:
    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg = SendGridAPIClient(SENDGRID_API_KEY) #()"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")
    # sg.set_sendgrid_data_residency("eu")
    # uncomment the above line if you are sending mail using a regional EU subuser
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)