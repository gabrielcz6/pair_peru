from pymongo import MongoClient
from dotenv import load_dotenv
import os,pandas as pd

class MongoDBInserter:
    def __init__(self, database_name="profilesdatabase", collection_name="profiles"):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # Obtener el URI de la variable de entorno
        uri = os.getenv("MONGODB_URI")
        
        # Inicializar la conexión a MongoDB
        self.client = MongoClient(uri)
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

    def insert_data(self, data):
        try:
            result = self.collection.insert_one(data)
            print(f"Documento insertado con id: {result.inserted_id}")
        except Exception as e:
            raise Exception(f"The following error occurred: {e}")
        finally:
            self.client.close()

    def get_all_users(self):
        try:
            # Recuperar todos los documentos
            users = list(self.collection.find())
            return users
        except Exception as e:
            raise Exception(f"Error while fetching users: {e}")
        finally:
            self.client.close()        



# Ejemplo de uso para convertir los usuarios en un DataFrame
