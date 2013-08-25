'''
Created on 2013-8-24

@author: hp
'''

import subprocess
import time
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    """
    p = subprocess.Popen('python chord.py -i ini', stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    print p.stdout.read()
    time.sleep(1)
    p.stdin.write('show ID')
    print p.stdout.read()
    p.kill()
    """
    maxv = []
    minv = []
    avg = []
    num = 0
    data = open("sample.txt")
    for line in data:
        tmp = map(int,line.split(','))
        maxv.append(max(tmp))
        minv.append(min(tmp))
        av = sum(tmp) / len(tmp)
        avg.append(av)
        num += 1
    err = np.row_stack((np.array(avg) -  np.array(minv),  np.array(maxv) -  np.array(avg)))
    plt.errorbar(range(1,num +1), avg, fmt='ro', yerr=err)
    plt.xticks(range(0, num +2))
    plt.yticks(range(min(minv) -1, max(maxv) +2))
    plt.xlabel(r'nodes')
    plt.ylabel(r'queries')
    plt.show()