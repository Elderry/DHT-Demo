from random import normalvariate
from random import randint
from math import fabs
from os.path import exists
from os import remove

keyNum = 100
valueSizeBound = [1, 100]
randomType = 'pure'
sqlFileName = 'initialize.sql'

sql = 'DROP TABLE if EXISTS key_value;\n'
sql += 'CREATE TABLE `test`.`key_value` ('
sql += '`keys` INT NOT NULL ,'
sql += '`values` LONGTEXT NULL ,'
sql += 'PRIMARY KEY (`keys`) );\n'

for i in range(keyNum):
    valueSize = randint(valueSizeBound[0], valueSizeBound[1])
    value = 'k' * valueSize
    sql += 'INSERT INTO `test`.`key_value` (`keys`, `values`) VALUES (' + str(i) + ', \'' + value + '\');\n'

if exists(sqlFileName):
    remove(sqlFileName)
    
sqlFile = open(sqlFileName, 'w')
sqlFile.write(sql)
sqlFile.close()
