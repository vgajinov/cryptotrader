import math



def woo(x,y):
    d = y - x
    p1 = math.floor(math.log10(x))
    p2 = math.floor(math.log10(d))
    #m = 10**(min(p1, p2))
    #xmin = x - x%m - m
    #ymax= y - y%m + m
    m = 10**(p2)
    xmin = int(x/m) * m
    if m == 1:
       xmin -= 1
    ymax = (int(y/m) + 1) * m
    print(x, y, p1, p2, xmin, ymax)


woo(4,16)
woo(14,18)
woo(14,167)
woo(145,167)
woo(145,147)
woo(0.14,0.16)
woo(0.013, 0.16)
woo(0.0345, 0.0467)

# delta = maxVal - minVal
# m = 10 ** (math.floor(math.log10(delta)))
# minVal = int(minVal / m) * m
# if m == 1:
#   minVal -= 1
# maxVal = (int(maxVal / m) + 1) * m