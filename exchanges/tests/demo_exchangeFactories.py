from exchanges.exchangeWSFactory import ExchangeWSFactory
from exchanges.exchangeRESTFactory import ExchangeRESTFactory



rest_exchanges = ExchangeRESTFactory.get_exchanges()
print()
print('REST clients:')
print('-'*40)
print(', '.join(rest_exchanges))

for ex in rest_exchanges:
   client = ExchangeRESTFactory.createClient(ex)
   print()
   print(ex, 'symbols:')
   print(client.symbols())




ws_exchanges = ExchangeWSFactory.get_exchanges()
print()
print('Websocket clients:')
print('-'*40)
print(','.join(ws_exchanges))

