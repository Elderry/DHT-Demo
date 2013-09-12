'''
Created on 2013-8-28

@author: hp
'''
import random
import math
import numpy as np
import matplotlib.pyplot as plt

'''calculate maximum, minimum and average keys and values per node when key-value is predetermined and all in a normal distribution'''
if __name__ == '__main__':
    nodelist = random.sample(range(0,1024),100)
    nodelist.sort()
    key = []
    value = []
    '''predetermine key-value mapping from the specific normal distribution'''
    mapped = [0 for n in range(10000)]
    for i in range(10000):
        x = int(math.fabs(random.normalvariate(5000, 1600)))
        key.append( x % 10000)
        y = int(math.fabs(random.normalvariate(0, 100)))
        value.append( y % 10000)
    for i in range(10000):
        if (key[i] % 1024) > nodelist[99]:
            mapped[i] = 0
        elif (key[i] % 1024) < nodelist[0]:
            mapped[i] = 99
        else:
            for j in range(100):
                if nodelist[j] >= (key[i] % 1024):
                    mapped[i] = j
                    break
    maxk = []
    mink = []
    maxv = []
    minv = []
    avgk = []
    avgv = []
    x = []
    counterlist = [0 for n in range(100)]
    valuelist = [0 for n in range(100)]
    '''calculate results when increasing key numbers'''
    for num in range(1,11):
        for k in range(1000 * num):
            tmp = random.randint(0, 9999)
            counterlist[mapped[tmp]] += 1
            valuelist[mapped[tmp]] += value[tmp]
        maxk.append(max(counterlist))
        mink.append(min(counterlist))
        avgk.append(sum(counterlist) / 100)
        maxv.append(max(valuelist))
        minv.append(min(valuelist))
        avgv.append(sum(valuelist) / 100)
        x.append(1000 * num)
        counterlist = [0 for n in range(100)]
        valuelist = [0 for n in range(100)]
    plt.subplot(2, 1, 1)
    err = np.row_stack((np.array(avgk) -  np.array(mink),  np.array(maxk) -  np.array(avgk)))
    plt.errorbar(x, avgk, fmt='ro', yerr=err)
    plt.ylabel(r'keys per node')
    plt.xlim(0, 11000)
    plt.ylim(0, max(maxk) +1)
    
    plt.subplot(2, 1, 2)
    err = np.row_stack((np.array(avgv) -  np.array(minv),  np.array(maxv) -  np.array(avgv)))
    plt.errorbar(x, avgv, fmt='ro', yerr=err)
    plt.xlabel(r'keys')
    plt.ylabel(r'values per node')
    plt.xlim(0, 11000)
    plt.ylim(0, max(maxv) +1)
    
    plt.show()