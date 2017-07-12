def _get_trade_proposals(quotes, technical_indicators):

   # we want to BUY when technical_indicators['psar_bear'] switches from value to None,
   # if there are AT LEAST N consecutives Nones
   consec_nones = 2
   init_offset = consec_nones
   numsamples = len(technical_indicators['psar_bear'])

   # get the indices of the None elements in array, whose preceding element is not None
   #for elem in technical_indicators['psar_bear']:
   buy_time_idx = []
   for i, j in enumerate(technical_indicators['psar_bear'][init_offset:]):
      real_i = i+init_offset
      window = max(real_i-consec_nones, 0)
      bear_starts = all([x is not None for x in technical_indicators['psar_bear'][window:real_i]]) and j is None
      if bear_starts:
         buy_time_idx.append(real_i)

   # get the indices of the None elements in array, whose next element is None
   sell_time_idx = []
   for i, j in enumerate(technical_indicators['psar_bull'][init_offset:]):
      real_i = i+init_offset
      window = max(real_i-consec_nones, 0)
      bull_starts = all([x is not None for x in technical_indicators['psar_bull'][window:real_i]]) and j is None
      if bull_starts:
         sell_time_idx.append(real_i)

   # generate an order book
   OrderBook = [ (quotes[i,0], 'B', quotes[i,1]) for i in buy_time_idx ] + [ (quotes[i,0], 'S', quotes[i,1]) for i in sell_time_idx ]
  
   #print OrderBook
   return sorted(OrderBook, key=lambda x: x[0])


# Basic strategy: Sell at the end of a bull trend and buy at the end of a bear trend
def basic_strategy(quotes, technical_indicators, capital, broker_fee=.002):
   coins=0

   OrderBook = _get_trade_proposals(quotes, technical_indicators)
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
def maskedBuy_strategy(quotes, technical_indicators, OrderBook, capital, broker_fee=.002):
   coins=0
   last_sametype_samples = 2

   OrderBook = _get_trade_proposals(quotes, technical_indicators)
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


