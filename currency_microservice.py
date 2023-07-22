import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
import pika
import json
import freecurrencyapi

def main():

    # Get API Key
    load_dotenv(find_dotenv())
    @dataclass(frozen=True)
    class APIkeys:
        API_key: str = os.getenv('API_key')

    # Input Validation List
    valid_currencies = ['EUR','USD','JPY','BGN','CZK','DKK','GBP','HUF','PLN','RON',
                        'SEK','CHF','ISK','NOK','HRK','RUB','TRY','AUD','BRL','CAD',
                        'CNY','HKD','IDR','IDR','ILS','INR','KRW','MXN','MYR','NZD',
                        'PHP','SGD','THB','ZAR']

    client = freecurrencyapi.Client(APIkeys.API_key)

    def get_status():
        return client.status()

    def get_currencies(list_curr):
        return client.currencies(list_curr)

    def get_latest(base, target):
        return client.latest(base, target)

    def get_historical(base, target, start_date, end_date):
        return client.historical(start_date, base, target)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #channel.queue_declare(queue='rpc_queue')
    channel.queue_declare(queue='request')
    channel.queue_declare(queue='response')

    def callback(channel, method, props, body):
        message = json.loads(body)
        print(message)
        if message.get('type') == 'status':
            response = get_status()
        elif message.get('type') == 'currencies':
            response = get_currencies(message.get('currencies'))
        elif message.get('type') == 'latest':
            response = get_latest(message.get('base'), message.get('target'))
        elif message.get('type') == 'historical':
            response = get_historical(message.get('base'),
                                      message.get('target'),
                                      message.get('start_date'),
                                      message.get('end_date'))
        else:
            print('Invalid request')
            return
        channel.basic_publish(exchange='', routing_key='response', body=json.dumps(response))
        #channel.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=json.dumps(response))
        #channel.basic_ack(delivery_tag=method.delivery_tag)

   # channel.basic_qos(prefetch_count=1)
    #channel.basic_consume(queue='rpc_queue', on_message_callback=callback)
    channel.basic_consume(queue='request',auto_ack=True,on_message_callback=callback)
    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')

#if request_currency not in valid_currencies:
    #raise Exception("Invalid Currency Request")

#Get data from pipe
    #desired request (latest, specific currencies, or historical)
    #base_currency  # default to USD if none provided
    #target_currency
    # perform data validation
    # pick appropriate request
    # make appropriate request
    # send result data back through pipe

#def get_latest(base_curr='USD', target_curr):



#print(client.status())

#result =
#print(result)

#latest_data = client.latest()
#print(latest_data)

#r2 = client.historical('2022-02-02')
#print(r2)

