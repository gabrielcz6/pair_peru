import json
from utils.db_connection.mongodb import MongoDBInserter
import pandas as pd
from utils.parse_combine_json import parse_json_from_string
import openai
import google.generativeai as genai
from dotenv import load_dotenv
import os



class jupiter_class:
 
 def __init__(self):
    self.clasemongo = MongoDBInserter()
    self.client = self.clasemongo.client
    self.db = self.client["profilesdatabase"]
    self.collection = self.db["profiles"]
    self.openai_key = "sk-6f"
    self.documentos=[]
    self.profiles=[]	
    self.documentos=self.collection.find()
    load_dotenv()
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

    
    for i, documento in enumerate(self.documentos, 1):
       self.profiles.append(documento)

 def simulate_preferencias(self, agent1, agent2):
     
    preferencias=agent1.generate_comparation(agent2)
    preferencias=parse_json_from_string(preferencias)
    if preferencias==None:
                score=0
    else:     
                score=len(preferencias)

    #guardando la conversacion y el score en la bd
    inserter= MongoDBInserter()
    inserter.insertar_preferencias_pairing(agent1.id_usuario,agent2.id_usuario,preferencias,score)            
    inserter.close_connection()
    return preferencias,score            
     
 def simulate_conversation(self, agent1, agent2, turns=3):
    """
    Simula una conversación entre dos agentes durante varios turnos.
    Retorna el historial de la conversación y un puntaje basado en la calidad.
    """
    conversation = []
    score = 0
    
    

    # Agente 1 inicia la conversación
    message = agent1.generate_message(agent2)
    conversation.append((agent1.id_usuario, message))
   
    for _ in range(turns):
        # Agente 2 responde
        response = agent2.respond_to_message(message)
        conversation.append((agent2.id_usuario, response))

        # Incrementar puntaje por temas comunes mencionados
        for key in ["lugares", "comidas", "hobbies"]:
            common_topics = set(agent1.__dict__[key]) & set(agent2.__dict__[key])
            score += sum(1 for topic in common_topics if topic in response)

        # Agente 1 responde al mensaje
        message = agent1.respond_to_message(response)
        conversation.append((agent1.id_usuario, message))

        # Incrementar puntaje por temas comunes mencionados
        for key in ["lugares", "comidas", "hobbies"]:
            common_topics = set(agent1.__dict__[key]) & set(agent2.__dict__[key])
            score += sum(1 for topic in common_topics if topic in message)

    #guardando la conversacion y el score en la bd
    inserter= MongoDBInserter()
    inserter.insertar_conversacion_pairing(agent1.id_usuario,agent2.id_usuario,conversation,score)
    #input("conversacion_display")
    conversacion_display=self.generar_conversacion_display(agent1,agent2)
    
    #insertando la conversacion display!
    inserter.insertar_conversacion_display(conversacion_display,agent1.id_usuario,agent2.id_usuario)
    inserter.close_connection()
    
    return conversation, score
 
 def find_top_matches_preferencia_pareja(self,selected_agent,agents):
    """
    Encuentra los top N matches para un agente seleccionado basados en sus preferencias.
    """
    ## Considerar solo agentes de sexo distinto
    sexo_selected_agent = selected_agent.sexo
    opposite_gender_agents = [perfil for perfil in agents if perfil.sexo == ("F" if sexo_selected_agent == "M" else "M")]
    matches = []
    inserter= MongoDBInserter()
    
    for agent in opposite_gender_agents:
       
       #primero verifica si ya fue evaluado sus preferencias respecto a la otra pareja
       if agent.id_usuario != selected_agent.id_usuario:  # Evitar autocomparación
       #aca se busca la conversacion y score, si es que existe en la bd (simulate_conversation)
           existpreferencias=inserter.busca_preferencias_pairing(selected_agent.id_usuario,agent.id_usuario)
           if existpreferencias != False:
               print("preferencias existente!")
               preferencias,score=existpreferencias
               
           else:
                  #si no encuentra a con b ni b con a crea nueva preferencias
                  preferencias,score=self.simulate_preferencias(selected_agent,agent)
                      
           #input(f"comparation sin filtro {agent.id_usuario}: \n\n {comparation}\n\n")
 
           matches.append((agent.id_usuario, score, preferencias))         
    return matches   


 def find_top_matches_conversation(self, selected_agent, agents):
    """
    Encuentra los top N matches para un agente seleccionado basados en conversaciones simuladas.
    """
    ## Considerar solo agentes de sexo distinto
    sexo_selected_agent = selected_agent.sexo
    opposite_gender_agents = [perfil for perfil in agents if perfil.sexo == ("F" if sexo_selected_agent == "M" else "M")]

    matches = []
    inserter= MongoDBInserter()

    for agent in opposite_gender_agents:
        
        if agent.id_usuario != selected_agent.id_usuario:  # Evitar autocomparación

            #aca se busca la conversacion y score, si es que existe en la bd (simulate_conversation)
            existconversation=inserter.busca_conversacion_pairing(selected_agent.id_usuario,agent.id_usuario)
            
            if existconversation != False:
               print("conversacion existente!")
               conversation,score=existconversation
            else:                
               existconversationviceversa=inserter.busca_conversacion_pairing(agent.id_usuario,selected_agent.id_usuario)
               
               if existconversationviceversa != False:
                  print("conversacion existente!")
                  conversation,score=existconversationviceversa
               else:
                  #si no encuentra a con b ni b con a crea nueva converesacion
                  conversation, score = self.simulate_conversation(selected_agent, agent)  
            
            print(agent.id_usuario)
           
            matches.append((agent.id_usuario, score, conversation))

    return matches
 
 def find_top_matches_final(self,usuario_seleccionado,top_matches_preferencia_pareja,top_matches_conversacion):
    #input(f"selected agent = {usuario_seleccionado}")
    #input(len(top_matches_preferencia_pareja))

    #input(len(top_matches_conversacion))

    # Generar lista final
    lista_final = []
    for item1 in top_matches_preferencia_pareja:
        for item2 in top_matches_conversacion:
            if item1[0] == item2[0]:  # Verificar si los usuarios son iguales
                usuario = item1[0]
                puntaje_promedio = (item1[1]*0.8 + item2[1]*0.2)
                preferencias_encontradas = item1[2]
                conversacion = item2[2]
                lista_final.append((usuario, puntaje_promedio, preferencias_encontradas, conversacion))
    
    #input(f"lista final: \n \n{lista_final}")
    df_matches = pd.DataFrame(columns=["perfil","score","preferencias_encontradas","conversacion"])
    i = 0
    for match in lista_final:
        df_matches.loc[i] = (match[0],match[1],match[2],match[3])
        i = i + 1
    df_matches.sort_values(by='score', ascending=False, inplace=True)
    df_matches.reset_index(drop=True, inplace=True)
    #input(df_matches)
    #guardar en la bd los matches finales
    
    inserter=MongoDBInserter()
    inserter.insertar_matches(usuario_seleccionado,df_matches.iloc[0]["perfil"],df_matches.iloc[1]["perfil"],df_matches.iloc[2]["perfil"])
    inserter.close_connection()

        
    #input(lista_final[1])
    return df_matches
    
 def generar_conversacion_display(self,usuario1,usuario2):
    """
    Utiliza GPT-4 para generar una buena conversacion para el display.
    """
    prompt = f"""
        Deberas generar un chat de whatsapp con las siguientes reglas:

        *La conversacion debe ser fluida y debe impactar a quien lo lee, debe tener un estilo calido como latino
        *La conversacion debe centrarse en sus cosas en comun, tratando de abarcar lo mayor posible en coincidencias
        *la conversacion debera tener de salida un json con la siguiente estructura:

         [
         ["user": "user":"{usuario1.id_usuario}","message": "mensaje del chat"],
         ["user": "user":{usuario2.id_usuario},"message": "mensaje del chat"],
         ]
        *La conversacion debe ser de 30 idas y vueltas
        *Los perfiles son los siguientes
         
        Tu perfil:
        - Nombre de usuario: {usuario1.id_usuario}
        - Trabajos: {', '.join(usuario1.trabajo)}
        - Estudio: {usuario1.estudio}
        - Lugares favoritos: {', '.join(usuario1.lugares)}
        - Comidas favoritas: {', '.join(usuario1.comidas)}
        - Hobbies: {', '.join(usuario1.hobbies)}

        El perfil de la persona con la que interactúas:
        - Nombre de usuario: {usuario2.id_usuario}
        - Trabajos: {', '.join(usuario2.trabajo)}
        - Estudio: {usuario2.estudio.get('carrera', 'No especificado')} con especialidad en {usuario2.estudio.get('especialidad', 'No especificado')}
        - Lugares favoritos: {', '.join(usuario2.lugares)}
        - Comidas favoritas: {', '.join(usuario2.comidas)}
        - Hobbies: {', '.join(usuario2.hobbies)}

        

    """
    # Llamada al modelo GPT-4
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en crear chats de whatsapp para una serie de tv, de gente que busca pareja en estados unidos, habla de manera divertida y jovial"},
            {"role": "user", "content": prompt}
        ]
    )


    # Devolver el texto generado por el modelo
    response_message = response.choices[0].message.content
    return response_message

 def summarize_profile_with_llm(self,usuario):

    
    """
    Utiliza GPT-4 para generar un resumen descriptivo de un perfil basado en sus características.
    """
    # Construir el prompt con los datos del perfil
    #input(self.profiles)
    profile = [perfil for perfil in self.profiles if perfil["id_usuario"] == usuario][0]
    
    prompt = f"""
    A continuación, tienes los detalles de un perfil:
    - Nombre de Usuario: {profile['id_usuario']}
    - Usuario de Instagram: {profile['ig_user']}
    - Trabajos: {', '.join(profile['trabajo'])}
    - Estudio: {profile['estudio'].get('carrera', 'No especificado')} con especialidad en {profile['estudio'].get('especialidad', 'No especificado')}
    - Lugares favoritos: {', '.join(profile['lugares'])}
    - Comidas favoritas: {', '.join(profile['comidas'])}
    - Hobbies: {', '.join(profile['hobbies'])}

    Con base en esta información, escribe un resumen atractivo y bien redactado que describa a esta persona. No asumas un nombre, para referirte a esa persona usa su Nombre de Usuario
    """
    # Llamada al modelo GPT-4
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en crear descripciones de perfiles personales."},
            {"role": "user", "content": prompt}
        ]
    )

    # Devolver el texto generado por el modelo
    response_message = response.choices[0].message.content
    return response_message
 ## Funciones para resumir

 def summarize_match_with_llm(self,selected_agent, matched_agent, conversation):
    """
    Envía la conversación completa a un LLM para generar un resumen de por qué es un buen match.
    """
    # Construir el historial de la conversación en formato texto
    conversation_text = "\n".join([f"{turn[0]}: {turn[1]}" for turn in conversation])

    # Crear el prompt para el modelo
    prompt = f"""
    A continuación, se muestra una conversación entre dos personas que están explorando si son compatibles como un buen match:

    Perfil de {selected_agent.id_usuario}:
    - Trabajos: {', '.join(selected_agent.trabajo)}
    - Estudio: {selected_agent.estudio.get('carrera', 'No especificado')} con especialidad en {selected_agent.estudio.get('especialidad', 'No especificado')}
    - Lugares favoritos: {', '.join(selected_agent.lugares)}
    - Comidas favoritas: {', '.join(selected_agent.comidas)}
    - Hobbies: {', '.join(selected_agent.hobbies)}

    Perfil de {matched_agent.id_usuario}:
    - Trabajos: {', '.join(matched_agent.trabajo)}
    - Estudio: {matched_agent.estudio.get('carrera', 'No especificado')} con especialidad en {matched_agent.estudio.get('especialidad', 'No especificado')}
    - Lugares favoritos: {', '.join(matched_agent.lugares)}
    - Comidas favoritas: {', '.join(matched_agent.comidas)}
    - Hobbies: {', '.join(matched_agent.hobbies)}

    Con base en la conversación y los perfiles de las personas, escribe un resumen explicando por qué estas dos personas son un buen match. Debe de ser un resumen corto. Condenza todas las ideas en un parrafo
    """
    #___
    self.model1 = genai.GenerativeModel("gemini-1.5-pro")
    response = self.model1.start_chat(
            history=[
                {"role": "model", "parts": "Eres un analista experto en relaciones y compatibilidad."},
                {"role": "user", "parts": prompt}
            ]
        )
    response_message = response.send_message(f"Conversación: {conversation_text}")
    return response_message.text






class GPTAgent:
    def __init__(self, profile):
        self.ig_user = profile["ig_user"]
        self.trabajo = profile["trabajo"]
        self.estudio = profile["estudio"]
        self.lugares = profile["lugares"]
        self.comidas = profile["comidas"]
        self.hobbies = profile["hobbies"]
        self.sexo = profile["genero"]
        self.id_usuario = profile["id_usuario"]
        self.preferencias_pareja= profile["preferencias_pareja"]

        self.model1 = genai.GenerativeModel("gemini-1.5-pro")

    def generate_comparation(self,other_agent):
       """
        Genera una comparacion semantica basado en mis preferencias como agente y las características del otro agente .
        """
       prompt = f"""
           REGLAS:
        * Deberas comparar Mi perfil con el perfil de la persona con la que interactuo y encontrar cosas en comun
        * deberas tomar en cuenta  Mis Preferencias de pareja ideal para generar la respuesta tambien
        * Todo este analisis debe ser cualitativo
        * La salida siempre debera ser un json con n elementos del siguiente formato:

       [
        {{
            "preferencia_encontrada": "Descripción de la compatibilidad por una preferencia",
            "sustento": "Explicación del porqué esa compatibilidad es relevante según los perfiles"
        }},
        ...
       ]

        Mi perfil:
        - Nombre de usuario: {self.id_usuario}
        - Usuario de Instagram: {self.ig_user}
        - Trabajos: {', '.join(self.trabajo)}
        - Estudio: {self.estudio.get('carrera', 'No especificado')} con especialidad en {self.estudio.get('especialidad', 'No especificado')}
        - Lugares favoritos: {', '.join(self.lugares)}
        - Comidas favoritas: {', '.join(self.comidas)}
        - Hobbies: {', '.join(self.hobbies)}
        
        Mis Preferencias de pareja ideal:

        - Personalidad: {self.preferencias_pareja.get('personalidad', 'No especificado')}\n"
        - Intereses: {self.preferencias_pareja.get('intereses', 'No especificado')}\n"
        - Importancia de la educación: {self.preferencias_pareja.get('importancia_educacion', 'No especificado')}\n"
        - Tipo de educación: {self.preferencias_pareja.get('tipo_educacion', 'No especificado')}\n"

        El perfil de la persona con la que interactúo:
        
        - Nombre de usuario: {other_agent.id_usuario}
        - Usuario de Instagram: {other_agent.ig_user}
        - Trabajos: {', '.join(other_agent.trabajo)}
        - Estudio: {other_agent.estudio.get('carrera', 'No especificado')} con especialidad en {other_agent.estudio.get('especialidad', 'No especificado')}
        - Lugares favoritos: {', '.join(other_agent.lugares)}
        - Comidas favoritas: {', '.join(other_agent.comidas)}
        - Hobbies: {', '.join(other_agent.hobbies)}

        """
       
       response = self.model1.start_chat(
            history=[
                {"role": "model", "parts": "Eres un experto en analizar compatibilidades entre 2 personas que buscan parejas ."},
                {"role": "user", "parts": prompt}
            ]
        )
       response_message = response.send_message(f"dame el json solo basandote en Mis Preferencias de pareja ideal")
       return response_message.text

    def generate_message(self, other_agent):
        """
        Genera un mensaje inicial basado en las características del otro agente.
        """
        prompt = f"""
        Tu perfil:
        - Nombre de usuario: {self.id_usuario}
        - Usuario de Instagram: {self.ig_user}
        - Trabajos: {', '.join(self.trabajo)}
        - Estudio: {self.estudio.get('carrera', 'No especificado')} con especialidad en {self.estudio.get('especialidad', 'No especificado')}
        - Lugares favoritos: {', '.join(self.lugares)}
        - Comidas favoritas: {', '.join(self.comidas)}
        - Hobbies: {', '.join(self.hobbies)}

        El perfil de la persona con la que interactúas:
        - Nombre de usuario: {other_agent.id_usuario}
        - Usuario de Instagram: {other_agent.ig_user}
        - Trabajos: {', '.join(other_agent.trabajo)}
        - Estudio: {other_agent.estudio.get('carrera', 'No especificado')} con especialidad en {other_agent.estudio.get('especialidad', 'No especificado')}
        - Lugares favoritos: {', '.join(other_agent.lugares)}
        - Comidas favoritas: {', '.join(other_agent.comidas)}
        - Hobbies: {', '.join(other_agent.hobbies)}

        """
        response = self.model1.start_chat(
            history=[
                {"role": "model", "parts": "Eres un asistente que genera conversaciones interesantes , esto no debe suponer nada, debera ser la conversacion optimizada ."},
                {"role": "user", "parts": prompt}
            ]
        )
        response_message = response.send_message(f"Escribe un mensaje inicial para iniciar una conversación interesante basada en temas en común,te prohibo palabras o frases genericos como listas con corchetes : [] dentro del texto.")
        return response_message.text

    def respond_to_message(self, incoming_message):
        """
        Responde a un mensaje recibido basado en las características del perfil.
        """
        prompt = f"""
        Tu perfil:
        - Nombre de usuario: {self.id_usuario}
        - Usuario de Instagram: {self.ig_user}
        - Trabajos: {', '.join(self.trabajo)}
        - Estudio: {self.estudio.get('carrera', 'No especificado')} con especialidad en {self.estudio.get('especialidad', 'No especificado')}
        - Lugares favoritos: {', '.join(self.lugares)}
        - Comidas favoritas: {', '.join(self.comidas)}
        - Hobbies: {', '.join(self.hobbies)}

        "

        Responde al mensaje, conectando con la persona y encontrando intereses en común, basándote solo en los datos disponibles en el texto.
        """
        response = self.model1.start_chat(
            history=[
                {"role": "model", "parts": "Eres un asistente que genera conversaciones interesantes solo basado en temas en común, te prohibo palabras o frases genericos como listas con corchetes : [] dentro del texto."},
                {"role": "user", "parts": prompt}
            ]
        )
        response_message = response.send_message(f"Mensaje recibido: {incoming_message}")
        return response_message.text