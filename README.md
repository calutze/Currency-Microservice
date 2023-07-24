# Currency-Microservice

## Request Format:
JSON format for all requests

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

