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

    def busca_conversacion_pairing(self, user1,user2):
        user1=user1
        user2=user2
        conversation_collection = self.database["conversations"]
        query={
            "id_user_agent1" : f"{user1}",
            "id_user_agent2" : f"{user2}",
             }
        documento = conversation_collection.find_one(query)
        

        # Comprobar si se encontró el documento y obtener el 'score'
        if documento is None:
            return False
            
        else:
            conversation_original = [(item["user"], item["message"]) for item in documento["conversation"]]
            return conversation_original,int(documento["score"])
        

    def insertar_conversacion_pairing(self, user1,user2,conversation,score):
        #guardando la conversacion y el score en la bd
        conversation_bd = [{"user": user, "message": message} for user, message in conversation]
        documento = {
        "id_user_agent1": f"{user1}",
        "id_user_agent2": f"{user2}",
         "conversation": conversation_bd,
         "score":f"{score}"
        }
        # Cambiar a la colección 'summary_profiles'
        conversation_collection = self.database["conversations"]
        result = conversation_collection.insert_one(documento)
        print(f"Documento de conversacion insertado con id: {result.inserted_id}")
        #input("subesubesube")


    def insert_resumen(self, data):
        try:
            # Cambiar a la colección 'summary_profiles'
            summary_collection = self.database["summary_profiles"]
            result = summary_collection.insert_one(data)
            print(f"Documento de resumen insertado con id: {result.inserted_id}")
        except Exception as e:
            raise Exception(f"The following error occurred: {e}")
        

    

    def get_resumen_by_id(self, id_usuario):
        try:
            # Cambiar a la colección 'summary_profiles'
            summary_collection = self.database["summary_profiles"]
            # Buscar el documento por id_usuario
            resumen = summary_collection.find_one({"id_usuario": id_usuario})
            
            if resumen!=None:
                return resumen["resumen"]  # Retorna el resumen si lo encuentra
            else:
                return False  # Retorna False si no encuentra el resumen
        except Exception as e:
            raise Exception(f"Error al buscar el resumen: {e}")
  

    def get_all_users(self):
        try:
            # Recuperar todos los documentos
            users = list(self.collection.find())
            return users
        except Exception as e:
            raise Exception(f"Error while fetching users: {e}")
    def close_connection(self):
        self.client.close()   



# Ejemplo de uso para convertir los usuarios en un DataFrame
