import psycopg2
import json
from psycopg2 import Error

def connect_to_db():
    """Conecta a la base de datos usando la configuración maestra de settings.json"""
    try:
        with open('settings.json', 'r') as file:
            config = json.load(file)
        
        db = config['db_config']

        connection = psycopg2.connect(
            host=db['host'],
            port=db['port'],
            database=db['dbname'],
            user=db['user'],
            password=db['password'],
            sslmode=db['sslmode']
        )
        return connection
    except (Exception, Error) as error:
        print(f"Error de conexión: {error}")
        return None