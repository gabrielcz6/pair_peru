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

        

    def busca_conversacion_pairing(self, user1, user2):
        user1 = user1
        user2 = user2
        conversation_collection = self.database["conversations"]
        
        # Primera búsqueda: user1 y user2
        query1 = {
            "id_user_agent1": f"{user1}",
            "id_user_agent2": f"{user2}",
        }
        
        # Segunda búsqueda: user2 y user1 (en caso de que no se encuentre la primera)
        query2 = {
            "id_user_agent1": f"{user2}",
            "id_user_agent2": f"{user1}",
        }
        
        # Intentar encontrar el documento con la primera búsqueda
        documento = conversation_collection.find_one(query1)
        
        # Si no se encuentra, intentar con la segunda búsqueda
        if documento is None:
            documento = conversation_collection.find_one(query2)
            user1temp = user1
            user2temp = user2
            user1 = user2temp
            user2 = user1temp


        
        # Comprobar si se encontró el documento y obtener el 'score'
        if documento is None:
            return False,user1temp,user2temp
        else:
            conversation_original = [(item["user"], item["message"]) for item in documento["conversation"]]
            return conversation_original, int(documento["score"]),user1,user2
        
    def busca_matches(self, user_id):
        # Seleccionando la base de datos y la colección
        profiles_collection = self.database["profiles"]
        # Definiendo el filtro para encontrar el documento específico
        filtro = {"id_usuario": user_id}
        # Buscando el documento
        documento = profiles_collection.find_one(filtro)
        # Comprobar si se encontró el documento y obtener los 'matches'
        if documento is None:
            return False
        else:
            return documento["match1"], documento["match2"]    
        
    def busca_sexo(self, user_id):
        # Seleccionando la base de datos y la colección
        profiles_collection = self.database["profiles"]
        # Definiendo el filtro para encontrar el documento específico
        filtro = {"id_usuario": user_id}
        # Buscando el documento
        documento = profiles_collection.find_one(filtro)
        # Comprobar si se encontró el documento y obtener los 'matches'
        if documento is None:
            return False
        else:
            return documento["genero"] 
            
    def insertar_matches(self, user_id, match1, match2):
      
       # Seleccionando la base de datos y la colección
       profiles_collection = self.database["profiles"]      
       # Definiendo el filtro para encontrar el documento específico
       filtro = {"id_usuario": user_id}    
       # Campos a añadir o modificar
       nuevos_campos = {
           "$set": {
               "match1": match1,
               "match2": match2
           }
       }
       
       # Actualizando el documento
       result = profiles_collection.update_one(filtro, nuevos_campos)
       
       # Mensaje de confirmación
       if result.matched_count > 0:
           print(f"Documento con ID {user_id} actualizado exitosamente.")
       else:
           print(f"No se encontró un documento con el ID {user_id}.")
   
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
