import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
import pika
import json
import freecurrencyapi
import requests

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def main():

    # Get API Key from .env file
    load_dotenv(find_dotenv())
    @dataclass(frozen=True)
    class APIkeys:
        API_key: str = os.getenv('API_key')

    # Input Validation List
    valid_currencies = ['EUR','USD','JPY','BGN','CZK','DKK','GBP','HUF','PLN','RON',
                        'SEK','CHF','ISK','NOK','HRK','RUB','TRY','AUD','BRL','CAD',
                        'CNY','HKD','IDR','IDR','ILS','INR','KRW','MXN','MYR','NZD',
                        'PHP','SGD','THB','ZAR']

    # Initialize freecurrencyapi client
    client = freecurrencyapi.Client(APIkeys.API_key)

    def get_status():
        """
        Returns the status from Freecurrency API listing the api call quotas
        """
        return client.status()

    def get_currencies(list_curr):
        """
        Returns the currency information from Freecurrency API for requested currencies
        """
        return client.currencies(list_curr)

    def get_latest(base, target):
        """
        Returns the latest exchange rates for given currencies
        """
        return client.latest(base, target)

    def get_historical(base, target, start_date, end_date):
        """
        Returns the historical exchange rates for a given time range
        """
        url = 'https://api.freecurrencyapi.com/v1/historical'
        response = requests.get(url, {'apikey': APIkeys.API_key,
                                      'date_from': start_date,
                                      'date_to': end_date,
                                      'base_currency': base,
                                      'currencies': target})
        content = json.loads(response.content)
        return content

    def currency_validation(list_curr):
        if list_curr is None:
            return True
        elif isinstance(list_curr, str):
            if list_curr not in valid_currencies:
                return False
        else:
            for request_curr in list_curr:
                if request_curr not in valid_currencies:
                    return False
        return True

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='request')
    channel.queue_declare(queue='response')

    def callback(channel, method, props, body):
        if not is_json(body):
            response = {'Error': 'Invalid Request'}
            channel.basic_publish(exchange='', routing_key='response', body=json.dumps(response))
            return

        message = json.loads(body)
        print(message)

        if message.get('type') == 'status':
            response = get_status()
        elif message.get('type') == 'currencies':
            if not currency_validation(message.get('currencies')):
                response = {'Error': 'Invalid Currency Requested'}
            else:
                response = get_currencies(message.get('currencies'))
        elif message.get('type') == 'latest':
            if (not currency_validation(message.get('base'))) or not (currency_validation(message.get('target'))):
                response = {'Error': 'Invalid Currency Requested'}
            else:
                response = get_latest(message.get('base'), message.get('target'))
        elif message.get('type') == 'historical':
            if (not currency_validation(message.get('base'))) or (not currency_validation(message.get('target'))):
                response = {'Error': 'Invalid Currency Requested'}
            else:
                response = get_historical(message.get('base'),
                                          message.get('target'),
                                          message.get('start_date'),
                                          message.get('end_date'))
        else:
            response = {'Error': 'Request not processed'}

        channel.basic_publish(exchange='', routing_key='response', body=json.dumps(response))

    channel.basic_consume(queue='request',auto_ack=True,on_message_callback=callback)
    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')



