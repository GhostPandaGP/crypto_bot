import requests

r = requests.get('https://api.bittrex.com/api/v1.1/public/getmarkethistory?market=USD-BTC')
print(r.status_code)