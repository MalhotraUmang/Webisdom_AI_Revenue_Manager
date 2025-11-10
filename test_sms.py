# Download the helper library from https://www.twilio.com/docs/python/install
# import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
# TWILIO_ACCOUNT_SID="AC46a3952ed4277698ee4db2dcaf111a4a"
# TWILIO_AUTH_TOKEN="2f31d8e591cd9301b6df129bfeb88f5e"
# account_sid = os.environ["AC46a3952ed4277698ee4db2dcaf111a4a"]
# auth_token = os.environ["2f31d8e591cd9301b6df129bfeb88f5e"]
account_sid = "AC46a3952ed4277698ee4db2dcaf111a4a"
auth_token = "2f31d8e591cd9301b6df129bfeb88f5e"
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="sms from twilio python",
    from_="+18782511984",
    to="+919986758671",
)

# Printing in backedn can be adapted.
# But actual sms sent has twilio specific template, due to trial account.
if(message.body=="Sent from your Twilio trial account - sms from twilio python"):
    message.body="sms from twilio python"


print(message.body)