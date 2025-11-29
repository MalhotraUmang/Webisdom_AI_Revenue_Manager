from dotenv import load_dotenv
import os
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)

# Load .env file
load_dotenv()

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  # content_sid='HX229f5a04fd0510ce1b071852155d3e75',
  # content_variables='{"1":"409173"}',
  body="whatsapp msg from twilio python",
  to='whatsapp:+919986758671'
)

# prints the correct message body, no twilio template observed.
print(message.body)
# print(message.sid)