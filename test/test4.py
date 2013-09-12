'''
Created on 2013-9-8

@author: hp
'''

from __future__ import division
import random
import hashlib
import string
import math
import numpy as np
import matplotlib.pyplot as plt 

'''use virtual node for load balance'''
if __name__ == '__main__':
    iniNodeNum = 1000
    keyNum = 100 * iniNodeNum
    scale = 2 ** 10
    mink = []
    maxk = []
    avg = []
    for j in range(1,11):
        nodeNum = iniNodeNum * j
        if scale <= nodeNum:
            scale *= 2
        nodelist = random.sample(range(0,scale),nodeNum)
        nodelist.sort()
        '''key number of virtual node'''
        counterlist = [0 for n in range(nodeNum)]
        for k in range(keyNum):
            seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
            sa = []
            for i in range(1024):
                sa.append(random.choice(seed))
            salt = string.join(sa)
            key = long(hashlib.sha1(salt).hexdigest(), 16) % (scale)
            if key > nodelist[nodeNum - 1]:
                counterlist[0] += 1
            elif key < nodelist[0]:
                counterlist[nodeNum -1] += 1
            else:
                low = 0
                high = nodeNum -1
                while high > low:
                    mid = int(math.ceil((high + low) /2))
                    if nodelist[mid] > key:
                        high = mid -1
                    elif nodelist[mid] < key:
                        low = mid +1
                    else:
                        break
                counterlist[low] += 1
        '''key number of real node'''
        sta = [0 for n in range(iniNodeNum)]
        for i in range(0,nodeNum,j):
            for cou in range(0,j):
                sta[i // j] += counterlist[i + cou]
        mink.append(min(sta))
        maxk.append(max(sta))
        avg.append(sum(sta) / len(sta))
    err = np.row_stack((np.array(avg) -  np.array(mink),  np.array(maxk) -  np.array(avg)))
    plt.errorbar(range(1,11), avg, fmt='ro', yerr=err)
    plt.xlim(0, 11)
    plt.ylim(0, max(maxk) +1)
    plt.ylabel(r'keys per node')
    plt.xlabel(r'virtual node number')
    plt.show()