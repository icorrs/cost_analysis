#consist data for mysql engine

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = 'nakamura7'
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'cost_analysis'

ENGINE_STR = (DIALECT+'+'+DRIVER+'://'+USERNAME
+':'+PASSWORD+'@'+HOSTNAME+':'+PORT+'/'+DATABASE
+'?charset=utf8')

DATA_DEFAULT = '201807'
