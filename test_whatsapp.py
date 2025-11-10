from twilio.rest import Client

account_sid = 'AC46a3952ed4277698ee4db2dcaf111a4a'
auth_token = '2f31d8e591cd9301b6df129bfeb88f5e'
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