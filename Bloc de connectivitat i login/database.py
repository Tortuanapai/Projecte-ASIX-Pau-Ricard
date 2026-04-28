import os
import psycopg2
import json
from psycopg2 import Error

def connect_to_db():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(base_dir, 'settings.json')

        with open(settings_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        
        db = config['db_config']

        connection = psycopg2.connect(
            host=db['host'],
            port=db['port'],
            database=db['dbname'],
            user=db['user'],
            password=db['password'],
            sslmode='require' 
        )

        cursor = connection.cursor()
        cursor.execute("SET search_path TO mask, hospital_blanes, public;")
        cursor.close()
        return connection

    except (Exception, Error) as error:
        print(f"Error de conexión: {error}")
        return None