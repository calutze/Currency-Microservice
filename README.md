# Currency-Microservice
Dependencies:
- os
- sys
- dotenv
- dataclasses
- pika
- json
- freecurrencyapi
- requests
- datetime

## Request Format:
Sample Request:
`connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='request')
latest_request = {"type": "latest", "base": "USD", target": ["CAD", "EUR"]}
message = json.dumps(latest_request)
channel.basic_publish(exchange='',
                      routing_key='request',
                      body=message)`
- JSON format for all requests
- RabbitMQ queue name for requests to the microservice is 'request'


### Status Request
{“type”: “status”}

### Currencies Request
request = {“type”: “currencies”, “currencies”: [“EUR”, “USD”, “CAD”]}
- "currencies" parameter is a list of currencies. Can be left blank (None), defaults to all currencies

### Latest Request
request = {“type”: “latest”, “base”: “USD”, “target”: [“CAD”, “EUR”]}
- base can be left blank (None), defaults to USD
- target can be left blank (None), defaults to all currencies

### Historical Request
request = {“type”: “historical”, “base”: “USD”, “target”: [“CAD”, “EUR”], “start_date”: “2022-02-02”, “end_date”: “2023-07-04”}
- start_date and end_date must be within 366 days of each other
- date format is YYYY-MM-DD
- base can be left blank (None), defaults to USD
- target can be left blank (None), defaults to all currencies

## Response Format
The microservice sends a b
- RabbitMQ queue name for responses from the microservice is 'response'

