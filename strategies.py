
# Basic strategy: Sell at the end of a bull trend and buy at the end of a bear trend
def basic_strategy(OrderBook, capital, broker_fee=.002):
   coins=0

   OrderBookOut = []
   for order in OrderBook:
      order_sent = False
      if order[1] == 'S' and coins>0:
         coins_sold=min(.2*coins, .5)
         capital += (order[2] * coins_sold)/(1+broker_fee)
         coins -= coins_sold
         order_sent = True
         
      if order[1] == 'B' and capital>0:
         invest = min(capital, 500)
         coins += invest / order[2]
         capital -= invest*(1+broker_fee)
         order_sent = True
     
      if order_sent:
         OrderBookOut.append(order)

   total_assets_value = capital + coins * OrderBook[-1][2]
   return total_assets_value, OrderBookOut


# Evolution from basic strategy: If buy order and on a descending trend, ignore the buy.
# same with a sell order in ascending trend
def maskedBuy_strategy(OrderBook, capital, broker_fee=.002):
   coins=0
   last_sametype_samples = 2

   OrderBookOut = []
   for order in OrderBook:
      order_sent = False
      if order[1] == 'S' and coins>0:
         coins_sold=min(.2*coins, .5)
         capital += (order[2] * coins_sold)/(1+broker_fee)
         coins -= coins_sold
         order_sent = True
         
      if order[1] == 'B' and capital>0:
         invest = min(capital, 500)
         coins += invest / order[2]
         capital -= invest*(1+broker_fee)
         order_sent = True
     
      if order_sent:
         OrderBookOut.append(order)

   total_assets_value = capital + coins * OrderBook[-1][2]
   return total_assets_value, OrderBookOut


