import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
import socket
import freecurrencyapi

load_dotenv(find_dotenv())
@dataclass(frozen=True)
class APIkeys:
    API_key: str = os.getenv('API_key')

#Get data from pipe
#base_currency  # default to USD if none provided
#target_currency

#def get_latest(base_curr='USD', target_curr):

client = freecurrencyapi.Client(APIkeys.API_key)

print(client.status())

result = client.currencies(currencies=['EUR', 'CAD'])
print(result)

latest_data = client.latest()
print(latest_data)

r2 = client.historical('2022-02-02')
print(r2)