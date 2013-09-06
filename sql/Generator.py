from random import normalvariate
from random import randint
from math import fabs
from os.path import exists
from os import remove

keyNum = 1000
valueSizeBound = [1, 100]
randomType = 'pure'
sqlFileName = 'initialize.sql'

sql = 'DROP TABLE if EXISTS key_value;\n'
sql += 'CREATE TABLE `test`.`key_value` ('
sql += '`mykey` INT NOT NULL ,'
sql += '`myvalue` LONGTEXT NULL ,'
sql += 'PRIMARY KEY (`mykey`) );\n'

for i in range(keyNum):
    valueSize = randint(valueSizeBound[0], valueSizeBound[1])
    value = 'k' * valueSize
    sql += 'INSERT INTO `test`.`key_value` (`mykey`, `myvalue`) VALUES (' + str(i) + ', \'' + value + '\');\n'

if exists(sqlFileName):
    remove(sqlFileName)
    
sqlFile = open(sqlFileName, 'w')
sqlFile.write(sql)
sqlFile.close()

print('Finished')
