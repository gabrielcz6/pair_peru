from pymongo import MongoClient
from dotenv import load_dotenv
from utils.parse_combine_json import parse_json_from_string
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

    def busca_conversacion_display_pairing(self, user1, user2):
        user1 = user1
        user2 = user2
        try: 
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
                  # Realizas la consulta con un filtro lógico
          conversation_collection = self.database["conversations"].find_one(query1)
          
          if conversation_collection==None:
              conversation_collection = self.database["conversations"].find_one(query2)
              if conversation_collection==None:
                  return False
              else :
                  conversation_original = [(item["user"], item["message"]) for item in conversation_collection["conversation_display"]]
                  return conversation_original
          else:    
              conversation_original = [(item["user"], item["message"]) for item in conversation_collection["conversation_display"]]
              return conversation_original
        except:
            return False
 


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
        
        # Comprobar si se encontró el documento y obtener el 'score'
        if documento is None:
            return False
        else:
            conversation_original = [(item["user"], item["message"]) for item in documento["conversation"]]
            return conversation_original, int(documento["score"])
        
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

    def insertar_conversacion_display(self,conversacion_display,user1,user2):
        conversacion_display=parse_json_from_string(conversacion_display)
        #input(f"conversacion \n\n{conversacion_display}")
        conversation_display_bd = [
        {"user": element["user"], "message": element["message"]} 
        for element in conversacion_display
        ]

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

        # Documento a insertar o actualizar
        nuevo_documento = {
        "conversation_display": conversacion_display,  # Agrega más campos si es necesario
                         }
        
        # Intentar encontrar el documento con la primera búsqueda
        documento = conversation_collection.find_one(query1)
        
     
        if documento != None:
           
            #entra con el query 1 a guardar
            resultado = conversation_collection.update_one(query1, {"$set": nuevo_documento}, upsert=True) 
            if resultado.upserted_id:
                print(f"Documento insertado con ID: {resultado.upserted_id}")
            else:
                print("Documento actualizado correctamente.")
            print("conversacion_display guardado")
        else:    
            documento = conversation_collection.find_one(query2)
            if documento!=None:
                #entra con el query 2 a guardar
                resultado = conversation_collection.update_one(query2, {"$set": nuevo_documento}, upsert=True)
                print("conversacion_display guardado")
                if resultado.upserted_id:
                  print(f"Documento insertado con ID: {resultado.upserted_id}")
                else:
                  print("Documento actualizado correctamente.")
            else:
                return False    



        #input(conversation_display_bd)

    def insert_resumen(self, data):
        try:
            # Cambiar a la colección 'summary_profiles'
            summary_collection = self.database["summary_profiles"]
            result = summary_collection.insert_one(data)
            print(f"Documento de resumen insertado con id: {result.inserted_id}")
        except Exception as e:
            raise Exception(f"The following error occurred: {e}")
        

    def insert_intereses(self,user,preferencias_pareja):
        #ejemplo:
        '''
        # Datos a insertar
        preferencias_pareja = {
        "personalidad": "amable, divertida, aventurera",
        "intereses": "deportes, lectura, viajes, cocina, arte",
        "importancia_educacion": "Muy importante",
        "tipo_educacion": "universitaria"
         }
        '''
        try:
            # Seleccionar la base de datos y la colección
            filtro = {"id_usuario": user}
            # Actualizar el documento, añadiendo el campo preferencias_pareja
            resultado = self.collection.update_one(
                filtro, 
                {"$set": {"preferencias_pareja": preferencias_pareja}}
            )

            if resultado.matched_count > 0:
              print("El documento preferencias se actualizó correctamente.")
              #print(f"Documentos modificados: {resultado.modified_count}")
        except Exception as e:
            raise Exception(f"Error insertando preferencias: {e}")  


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
