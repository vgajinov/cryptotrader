import numpy as np
from scipy.ndimage.filters import convolve1d
from scipy.signal import exponential


def ATR(quote_list, n):
   PC = np.roll(quote_list[:,4], 1)
   PC[0] = PC[1]
   h = quote_list[:,2]
   l = quote_list[:,3]
   TR = np.maximum(h - l, abs(h - PC), abs(l - PC))

   #initialize ATR array
   ATR = np.ndarray(shape=PC.shape, dtype=float)
   ATR[0] = np.mean(TR[:n])

   for i in range(1, quote_list.shape[0]):
      ATR[i] = ( (n - 1) * ATR[i - 1] + TR[i] ) / n

   return ATR


def moving_average(a, n=3, type='simple') :
   if type=='simple':
      weights = np.ones(n)
   else:
      weights = exponential(n, 0, -(n-1) / np.log(0.01), False)
   weights /= weights.sum()
   weights = np.concatenate((np.zeros(n), weights))

   return convolve1d(a, weights)


def KELCH(quote_list, n):
   average_hlc = np.asarray([(x[2] + x[3] + x[4])/3 for x in quote_list], dtype=float)
   average_hlc = quote_list[:,4]
   KelChM = moving_average( average_hlc, n=n, type='exp')
   atr_tmp = ATR(quote_list, n)
   KelChU = KelChM + 2 * atr_tmp
   KelChL = KelChM - 2 * atr_tmp

   return { "KELCH_average": KelChM, "KELCH_upper": KelChU, "KELCH_lower" : KelChL}


def parabolic_sar(quote_list, iaf = 0.02, maxaf = 0.2):
   length = quote_list.shape[0]
	 #format: d o h l c
   high = quote_list[:,2]
   low = quote_list[:,3]
   close = quote_list[:,4]
   #psar = close[:]
   psar = np.ndarray(shape=close.shape, dtype=float)
   psar[:2] = close[:2]
   psarbull = [None] * length
   psarbear = [None] * length
   bull = True
   af = iaf
   ep = low[0]
   hp = high[0]
   lp = low[0]
   for i in range(2,length):
      if bull:
         psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
      else:
         psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
      reverse = False
      if bull:
         if low[i] < psar[i]:
            bull = False
            reverse = True
            psar[i] = hp
            lp = low[i]
            af = iaf
      else:
         if high[i] > psar[i]:
            bull = True
            reverse = True
            psar[i] = lp
            hp = high[i]
            af = iaf
      if not reverse:
         if bull:
            if high[i] > hp:
               hp = high[i]
               af = min(af + iaf, maxaf)
            if low[i - 1] < psar[i]:
               psar[i] = low[i - 1]
            if low[i - 2] < psar[i]:
               psar[i] = low[i - 2]
         else:
            if low[i] < lp:
               lp = low[i]
               af = min(af + iaf, maxaf)
            if high[i - 1] > psar[i]:
               psar[i] = high[i - 1]
            if high[i - 2] > psar[i]:
               psar[i] = high[i - 2]
      if bull:
         psarbull[i] = psar[i]
      else:
         psarbear[i] = psar[i]

   return {"psar":psar, "psarbear":psarbear, "psarbull":psarbull}
