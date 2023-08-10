import os
import sys
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
import pika
import json
import freecurrencyapi
import requests
from datetime import datetime


def is_json(myjson):
    """
    Returns true if input is a valid json
    """
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def currency_validation(list_curr):
    """
    Checks if requested currency(s) is in valid currency list
    """
    # Valid Currency List
    valid_currencies = ['EUR', 'USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON',
                        'SEK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB', 'TRY', 'AUD', 'BRL', 'CAD',
                        'CNY', 'HKD', 'IDR', 'IDR', 'ILS', 'INR', 'KRW', 'MXN', 'MYR', 'NZD',
                        'PHP', 'SGD', 'THB', 'ZAR']
    # If blank
    if list_curr is None:
        return True

    # If single currency provided
    elif isinstance(list_curr, str):
        if list_curr not in valid_currencies:
            return False

    else:
        for request_curr in list_curr:
            if request_curr not in valid_currencies:
                return False
    return True


@dataclass(frozen=True)  # decorator makes keys immutable
class APIkeys:
    load_dotenv(find_dotenv())
    API_key: str = os.getenv('API_key')


def get_status(client):
    """
    Returns the status from Freecurrency API listing the api call quotas
    """
    return client.status()


def request_currencies(client, message):
    """
    Returns currency data request from Freecurrency API
    """
    if not currency_validation(message.get('currencies')):
        response = {'Error': 'Invalid Currency Requested'}
    else:
        response = get_currencies(client, message.get('currencies'))
    return response


def get_currencies(client, list_curr):
    """
    Returns the currency information from Freecurrency API for requested currencies
    """
    return client.currencies(list_curr)


def request_latest(client, message):
    """
     Returns latest data request from Freecurrency API
     """
    if not currency_validation(message.get('base')) or \
            not currency_validation(message.get('target')):
        response = {'Error': 'Invalid Currency Requested'}
    else:
        response = get_latest(client, message.get('base'), message.get('target'))
    return response


def get_latest(client, base, target):
    """
    Returns the latest exchange rates for given currencies
    """
    return client.latest(base, target)


def request_historical(message):
    """
     Returns historical data request from Freecurrency API
     """
    if not currency_validation(message.get('base')) or \
            not currency_validation(message.get('target')):
        response = {'Error': 'Invalid Currency Requested'}
    else:
        response = get_historical(message.get('base'), message.get('target'),
                                  message.get('start_date'), message.get('end_date'))
    return response


def get_historical(base, target, start_date, end_date):
    """
    Returns the historical exchange rates for a given time range
    """
    # Confirm dates are within 366 days max of each other
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d').date()
    delta = end_datetime - start_datetime
    if delta.days > 366:
        response = {'Error': 'Invalid Date Range, must be less than 366 days apart'}
        return response

    url = 'https://api.freecurrencyapi.com/v1/historical'
    response = requests.get(url, {'apikey': APIkeys.API_key, 'date_from': start_date,
                                  'date_to': end_date, 'base_currency': base, 'currencies': target})
    content = json.loads(response.content)
    return content


def main():
    # Initialize freecurrencyapi client
    client = freecurrencyapi.Client(APIkeys.API_key)

    def callback(ch, method, props, body):
        if not is_json(body):
            response = {'Error': 'Invalid Request'}
            channel.basic_publish(exchange='', routing_key='response', body=json.dumps(response))
            return
        message = json.loads(body)
        print(message)
        if message.get('type') == 'status':
            response = get_status(client)
        elif message.get('type') == 'currencies':
            response = request_currencies(client, message)
        elif message.get('type') == 'latest':
            response = request_latest(client, message)
        elif message.get('type') == 'historical':
            response = request_historical(message)
        else:
            response = {'Error': 'Request not processed'}
        channel.basic_publish(exchange='', routing_key='response', body=json.dumps(response))

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='request')
    channel.queue_declare(queue='response')
    channel.basic_consume(queue='request', auto_ack=True, on_message_callback=callback)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
