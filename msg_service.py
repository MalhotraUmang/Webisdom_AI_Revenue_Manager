##############################################################################################################
# 3 separate functions to send out SMS, WhatsApp and Email
#=============================================================================================================
# SMS:
# 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN' should be fetched from config.py
    # If possible from OS environment (.env)
# Message 'body', 'from_' and 'to' fields should be trigger_sms() function arguments
#=============================================================================================================
# WhatsApp:
# 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN' should be fetched from config.py
    # If possible from OS environment (.env)
# Message 'body', 'from_' and 'to' fields should be trigger_whatsapp_msg() function arguments
#=============================================================================================================
# Email:
# SENDGRID_API_KEY should be fetched from config.py
    # If possible from OS environment (.env)
# 'from_email', 'to_emails', 'subject', and 'emailText' fields should be trigger_email() function arguments
##############################################################################################################
# import os
from datetime import datetime, time as dtime
from twilio.rest import Client
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    # SENDGRID_API_KEY,
)

# MSG_BODY="!!! test sms from twilio !!!"
MSG_FROM="+18782511984",
# MSG_TO="+919986758671",

def trigger_sms(msg_body, msg_from, msg_to, msg_time):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # match msg_time with current time
    now = datetime.now().time()

    # Safely handle msg_time (can be str, time, or None)
    parsed_time = None
    if isinstance(msg_time, dtime):
        parsed_time = msg_time
    elif isinstance(msg_time, str) and msg_time.strip():
        for fmt in ("%H:%M", "%I:%M %p", "%H.%M", "%I.%M %p"):
            try:
                parsed_time = datetime.strptime(msg_time.strip(), fmt).time()
                break
            except ValueError:
                continue

    if parsed_time and now >= parsed_time:
        message = client.messages.create(
            body=msg_body,
            # from_=msg_from,
            # to=msg_to,
            from_=MSG_FROM,
            to=msg_to,
        )
        print("✅"f"📤 [SMS SENT] From: {msg_from} | To: {msg_to} | Msg: {msg_body[:50]}...")
    elif parsed_time:
        print(f"⏳ Not time yet — current: {now.strftime('%H:%M:%S')} < scheduled: {parsed_time.strftime('%H:%M')}")
    else:
        print(f"⚠️ Invalid msg_time ({msg_time}) — skipping send.")
        # print(" !!! TIMING DIDNT MATCH !!!")

    # Display the SMS message text in terminal.
    # print(message.body)
    # print("✅"f"📤 [SMS SENT] From: {msg_from} | To: {msg_to} | Msg: {msg_body[:50]}...")









# def trigger_whatsapp_msg(msg_body, msg_from, msg_to):
#     pass

# def trigger_email(mail_from, mail_to, mail_sub, mail_text):
#     pass
