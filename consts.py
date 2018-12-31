#consist data for mysql engine

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'myweb'
PASSWORD = '696139'
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'cost_analysis'

ENGINE_STR = (DIALECT+'+'+DRIVER+'://'+USERNAME
+':'+PASSWORD+'@'+HOSTNAME+':'+PORT+'/'+DATABASE
+'?charset=utf8')

DATE_DEFAULT = '201812'
