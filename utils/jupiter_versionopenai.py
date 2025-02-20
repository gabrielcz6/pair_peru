import json
from utils.db_connection.mongodb import MongoDBInserter
import pandas as pd
import openai


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
    
    for i, documento in enumerate(self.documentos, 1):
       self.profiles.append(documento)

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
     
    return conversation, score

 def find_top_matches(self, selected_agent, agents):
    """
    Encuentra los top N matches para un agente seleccionado basados en conversaciones simuladas.
    """
    ## Considerar solo agentes de sexo distinto
    sexo_selected_agent = selected_agent.sexo
    opposite_gender_agents = [perfil for perfil in agents if perfil.sexo == ("F" if sexo_selected_agent == "M" else "M")]

    matches = []
    for agent in opposite_gender_agents:
        

        if agent.id_usuario != selected_agent.id_usuario:  # Evitar autocomparación

            #aca se busca la conversacion y score, si es que existe en la bd (simulate_conversation)
            inserter= MongoDBInserter()
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

    # Ordenar por puntaje
    matches = sorted(matches, key=lambda x: x[1], reverse=True)

    return matches
 
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

    Conversación:
    {conversation_text}

    Con base en la conversación y los perfiles de las personas, escribe un resumen explicando por qué estas dos personas son un buen match. Debe de ser un resumen corto. Condenza todas las ideas en un parrafo
    """
    # Enviar el prompt al modelo
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Eres un analista experto en relaciones y compatibilidad."},
            {"role": "user", "content": prompt}
        ]
    )

    # Obtener el resumen generado por el modelo
    response_message = response.choices[0].message.content
    return response_message





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

        Escribe un mensaje inicial para iniciar una conversación interesante basada en temas en común.
        """
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera conversaciones interesantes."},
                {"role": "user", "content": prompt}
            ]
        )
        response_message = response.choices[0].message.content
        return response_message

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

        Mensaje recibido: "{incoming_message}"

        Responde al mensaje, conectando con la persona y encontrando intereses en común.
        """
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente que responde a mensajes en conversaciones."},
                {"role": "user", "content": prompt}
            ]
        )
        response_message = response.choices[0].message.content
        return response_message