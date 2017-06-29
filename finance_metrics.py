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
   KelChU = KelChM + 2 * ATR(quote_list, n)
   KelChL = KelChM - 2 * ATR(quote_list, n)

   return { "average": KelChM, "upper": KelChU, "lower" : KelChL}


