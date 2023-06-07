import os
from twilio.rest import Client


os.environ['AC63c327658e9b1387a94c3a3ec5a2a2b1'] = 'your_twilio_account_sid'


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['AC63c327658e9b1387a94c3a3ec5a2a2b1']
auth_token = os.environ['5d03ab0598e4baeb4e1016c9358721ca']
client = Client(account_sid, auth_token)

message = client.messages.create(
                              from_='whatsapp:+14155238886',
                              body='Hello, there!',
                              to='whatsapp:+15005550006'
                          )

print(message.sid)