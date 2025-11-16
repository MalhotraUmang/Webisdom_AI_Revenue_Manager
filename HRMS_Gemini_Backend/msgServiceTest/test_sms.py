# Download the helper library from https://www.twilio.com/docs/python/install
from dotenv import load_dotenv
import os
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)

# Load .env file
load_dotenv()

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="sms from twilio python",
    from_="+18782511984",
    to="+919986758671",
)

# Printing in backend can be adapted.
# But actual sms sent has twilio specific template, due to trial account.
if(message.body=="Sent from your Twilio trial account - sms from twilio python"):
    message.body="sms from twilio python"

print(message.body)