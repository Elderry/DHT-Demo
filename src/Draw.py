'''
Created on 2013-8-24

@author: hp
'''

import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    maxv = []
    minv = []
    avg = []
    num = 0
    data = open("sample.txt")
    for line in data:
        if not line.strip():
            if num != 0:
                maxv.append(0)
                minv.append(0)
                avg.append(0)
                num += 1
            continue
        sta = line.split(',')
        sta.pop()
        tmp = map(int,sta)
        maxv.append(max(tmp))
        minv.append(min(tmp))
        av = sum(tmp) / len(tmp)
        avg.append(av)
        num += 1
    err = np.row_stack((np.array(avg) -  np.array(minv),  np.array(maxv) -  np.array(avg)))
    plt.errorbar(range(1,num +1), avg, fmt='ro', yerr=err)
    plt.xlim(0, num +1)
    plt.ylim(0, max(maxv) +1)
    plt.xlabel(r'nodes')
    plt.ylabel(r'queries')
    plt.show()
    data.close()