# Currency-Microservice

## Request Format:
JSON format for all requests

### Status Request
{“type”: “status”}

### Currencies Request
"currencies" parameter is a list of currencies. Can be left blank (None), defaults to all currencies
{“type”: “currencies”, “currencies”: [“EUR”, “USD”, “CAD”]}

### Latest Request
- base can be left blank (None), defaults to USD
- target can be left blank (None), defaults to all currencies
{“type”: “latest”, “base”: “USD”, “target”: [“CAD”, “EUR”]}
- 
### Historical Request
- start_date and end_date must be within 366 days of each other
- date format is YYYY-MM-DD
- base can be left blank (None), defaults to USD
- target can be left blank (None), defaults to all currencies
{“type”: “historical”, “base”: “USD”, “target”: [“CAD”, “EUR”], “start_date”: “2022-02-02”, “end_date”: “2023-07-04”}
