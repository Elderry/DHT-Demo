'''
Created on 2013-9-3

@author: hp
'''

import matplotlib.pyplot as plt

'''collect statistics from data directory'''
if __name__ == '__main__':
    filelist = ['Alice','Bob','Candy','David','Eric','Frank','Grace','Harry','Iliana','Intial','Jason','Kate','Lucy','Maria','Nate','Olive','Panny','Quiana','Rayne','Shelley']
    datalist = []
    for i in range(len(filelist)):
        file = open(filelist[i] + '.log')
        counter =0
        data = []
        for line in file:
            counter += 1
            if counter % 2 == 0:
                data.append(line.strip())
        datalist.append(data)
        print data
        data = []
        file.close()
    for i in range(len(datalist)):
        data = datalist[i]
        plt.plot(range(len(data)),data)
    plt.ylabel(r'keys')
    plt.xlabel(r'time')
    plt.show()