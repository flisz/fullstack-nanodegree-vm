ENGINE = 'postgres'
USER = 'vagrant'
PASSWORD = None
if PASSWORD is None:
	USER_PASSWORD = USER
else: 
	USER_PASSWORD = USER + ':' + PASSWORD

HOST = 'localhost'
PORT = 5432

if PORT is None:
	HOST_PORT = HOST
else:
	HOST_PORT = HOST + ':' + str(PORT)

DB_NAME = 'restaurant'
POSTGRES_LOGIN = DB_NAME
SQL_COMMAND = '{}:///{}'.format(ENGINE,POSTGRES_LOGIN)
print('Using SQL_COMMAND: {}'.format(SQL_COMMAND))