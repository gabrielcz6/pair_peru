import streamlit as st
from perfilanalyzer import PerfilAnalyzer
import time
import pandas as pd
from utils.db_connection.mongodb import MongoDBInserter
from utils.jupiter import jupiter_class, GPTAgent
from streamlit_option_menu import option_menu
import os,re

def formatear_preferencias(preferencias):
    preferencias_str = "Preferencias Encontradas:\n\n"
    try:
     for i, pref in enumerate(preferencias, 1):
         preferencias_str += f"{i}. {pref['preferencia_encontrada']}\n"
         preferencias_str += f"   - {pref['sustento']}\n\n"

     return preferencias_str
    except:
        return preferencias

def getusersdict():
    inserter=MongoDBInserter()
    profiles = inserter.get_all_users()
    inserter.close_connection()
    return profiles

def cargar_usuarios_a_dataframe():
    """
    Carga los datos de usuarios desde MongoDB, los convierte a un DataFrame 
    y los guarda en session_state bajo la clave 'df_usuarios'.
    
    Returns:
        list: Lista de IDs de usuarios.
    """
    # Crear instancia de MongoDBInserter
    inserter = MongoDBInserter()
    
    try:
        # Obtener todos los usuarios desde la base de datos
        users = inserter.get_all_users()
        
        # Convertir los datos a un DataFrame
        df_usuarios = pd.DataFrame(users)
        
        # Filtrar columnas relevantes y guardar en session_state
        st.session_state.df_usuarios = df_usuarios[[
            "id_usuario", "genero", "trabajo", "estudio", "hobbies", "lugares", "comidas","preferencias_pareja"
        ]]

    finally:
        # Asegurar el cierre de la conexión a la base de datos
        inserter.close_connection()

        
        # Retornar lista de IDs de usuarios
        return st.session_state.df_usuarios

def cargar_usuarios_a_session_state():
    """
    Carga los datos de usuarios desde MongoDB, los convierte a un DataFrame 
    y los guarda en session_state bajo la clave 'df_usuarios'.
    
    Returns:
        list: Lista de IDs de usuarios.
    """
    # Crear instancia de MongoDBInserter
    inserter = MongoDBInserter()
    
    try:
        # Obtener todos los usuarios desde la base de datos
        users = inserter.get_all_users()
        
        # Convertir los datos a un DataFrame
        df_usuarios = pd.DataFrame(users)
        
        # Filtrar columnas relevantes y guardar en session_state
        st.session_state.df_usuarios = df_usuarios[[
            "id_usuario", "ig_user", "linkedin_user", "genero", "trabajo", "estudio", "hobbies", "lugares", "comidas"
        ]]
        
        
        # Retornar lista de IDs de usuarios
        return st.session_state.df_usuarios["id_usuario"].tolist()
    
    finally:
        # Asegurar el cierre de la conexión a la base de datos
        inserter.close_connection()

def generar_resumen(usuario_id):
    inserter=MongoDBInserter()
    resumen= inserter.get_resumen_by_id(usuario_id)
    
    if resumen:
        print("resumen recuperado de la bd")
        st.write(resumen)    
    else:
        jupiter_instance = jupiter_class()
        resumen = jupiter_instance.summarize_profile_with_llm(usuario_id)
        resumen_bd = {"id_usuario": f"{usuario_id}","resumen": f"""{resumen}"""}
        inserter.insert_resumen(resumen_bd)
        st.write(resumen)
        inserter.close_connection()

def editar_preferencias():
    inserter=MongoDBInserter() 
    # Botón para cargar los usuarios
    if st.button("Ver todos los usuarios"):
        # Guardar en session_state
        st.session_state.df_usuarios = cargar_usuarios_a_dataframe()

    # Mostrar la tabla si está en session_state
    if "df_usuarios" in st.session_state:
        st.write(st.session_state.df_usuarios)
        st.session_state.usuario_seleccionado = None
        # Mostrar el selectbox para seleccionar un usuario
        usuario_seleccionado = st.selectbox(
            "Selecciona tu usuario",
            st.session_state.df_usuarios["id_usuario"].tolist(),
                index=0 if st.session_state.usuario_seleccionado is None else st.session_state.df_usuarios["id_usuario"].tolist().index(st.session_state.usuario_seleccionado)
        )
        
        # Si el usuario seleccionado cambia, se actualiza session_state y se reflejará en el selectbox
        if usuario_seleccionado != st.session_state.usuario_seleccionado:
            st.session_state.usuario_seleccionado = usuario_seleccionado

    # Pregunta 1: Describe la personalidad ideal de tu pareja
    st.subheader("Describe la personalidad de tu pareja ideal con algunos adjetivos:")
    personalidad = st.text_input("Ejemplo: amable, divertida, aventurera")
    
    # Pregunta 2: Intereses, pasiones y pasatiempos
    st.subheader("Fuera del trabajo, ¿cuáles son algunos intereses, pasiones y pasatiempos que te parecen atractivos en una relación?")
    intereses = st.text_input("Ejemplo: deportes, lectura, viajes, cocina, arte")
    
    # Pregunta 3: Importancia de la educación
    st.subheader("¿Cuán importante es la educación de tu pareja ideal?")
    educacion_importancia = st.select_slider(
        "Selecciona un nivel de importancia:",
        options=["Nada importante", "Poco importante", "Moderadamente importante", "Muy importante", "Esencial"]
    )
    
    # Pregunta 4: Tipo de educación ideal
    st.subheader("¿Qué tipo de educación te gustaría que tenga tu pareja ideal?")
    tipo_educacion = st.text_input("Ejemplo: universitaria, técnica, autodidacta")
    
    # Botón para enviar
    if st.button("Enviar"):
        st.success("¡Tus preferencias han sido guardadas con éxito!")

        preferencias_pareja = {
        "personalidad": personalidad,
        "intereses": intereses,
        "importancia_educacion": educacion_importancia,
        "tipo_educacion": tipo_educacion
    }
        inserter.insert_intereses(st.session_state.usuario_seleccionado,preferencias_pareja)
        inserter.close_connection()
        st.write("### Resumen de tus respuestas:")
        st.write(f"- **Personalidad ideal**: {personalidad}")
        st.write(f"- **Intereses y pasatiempos atractivos**: {intereses}")
        st.write(f"- **Importancia de la educación**: {educacion_importancia}")
        st.write(f"- **Tipo de educación deseada**: {tipo_educacion}")
   
    
#DEL MENU PRINCIPAL

# Función para agregar un nuevo usuario
def agregar_usuario():
    st.header("Agregar Redes Sociales")
    
    #Formulario para datos de scrapping
    nombre_usuario = st.text_input("Nombre")
    cuenta_instagram = st.text_input("Cuenta Instagram")
    cuenta_linkedin = st.text_input("Cuenta Linkedin")
    gender = st.selectbox("Género", ["Selecciona...", "F", "M"])

    if st.button("Agregar usuario"):
        # Mostrar mensaje de carga
        with st.spinner('Cargando perfil...'):
            try:
                # Aquí se realiza el análisis del perfil con los parámetros proporcionados
                perfil = PerfilAnalyzer(cuenta_instagram, cuenta_linkedin, gender, nombre_usuario)  # Ajusta el id único según sea necesario
                file_path = perfil.analizar_perfil()
                time.sleep(5)
                # Si todo va bien, mostrar un mensaje de éxito
                st.success(f"Usuario {nombre_usuario} agregado con éxito!")
            
            except Exception as e:
                # Si ocurre un error, mostrar un mensaje de error
                st.error(f"Error al agregar al usuario {nombre_usuario}. Detalles: {e}")
    
# Función principal
def mostrar_usuarios():
    st.header("Panel de Usuarios")

    # Botón para cargar los usuarios
    if st.button("Ver todos los usuarios"):
        # Guardar en session_state
        st.session_state.df_usuarios = cargar_usuarios_a_dataframe()

    # Mostrar la tabla si está en session_state
    if "df_usuarios" in st.session_state:
        st.write(st.session_state.df_usuarios)
        st.session_state.usuario_seleccionado = None
        # Mostrar el selectbox para seleccionar un usuario
        usuario_seleccionado = st.selectbox(
            "Selecciona usuario",
            st.session_state.df_usuarios["id_usuario"].tolist(),
                index=0 if st.session_state.usuario_seleccionado is None else st.session_state.df_usuarios["id_usuario"].tolist().index(st.session_state.usuario_seleccionado)
        )
        
        # Si el usuario seleccionado cambia, se actualiza session_state y se reflejará en el selectbox
        if usuario_seleccionado != st.session_state.usuario_seleccionado:
            st.session_state.usuario_seleccionado = usuario_seleccionado

        if st.button("Generar resumen para el usuario seleccionado"):
            with st.spinner(f"Generando resumen para el usuario con ID {st.session_state.usuario_seleccionado}"):
             
             generar_resumen(st.session_state.usuario_seleccionado)

# Función para hacer pairing entre usuarios
def proceso_pairing():
    st.header("Pairing")
    # Aquí puedes incluir la lógica para hacer el pairing entre usuarios
    st.write("Aquí puedes hacer el pairing entre usuarios.")

    # Seleccionar un usuario con manejo de estado
    if "usuario_seleccionado" not in st.session_state:
            st.session_state.usuario_seleccionado = None
    
    profiles= getusersdict()
    st.session_state.df_usuarios = cargar_usuarios_a_dataframe()



    st.session_state.usuario_seleccionado = st.selectbox(
            "Selecciona usuario",
            st.session_state.df_usuarios["id_usuario"].tolist(),
            index=0 if st.session_state.usuario_seleccionado is None else st.session_state.df_usuarios["id_usuario"].tolist().index(st.session_state.usuario_seleccionado)
        )
    if st.button("Realizar Pairing"):
            with st.spinner(f"Generando pairing para el usuario con ID {st.session_state.usuario_seleccionado}"):
                
                
                # Crear agentes
                agents = [GPTAgent(profile) for profile in profiles]
                for agent in agents:
                  if agent.id_usuario == st.session_state.usuario_seleccionado:
                     selected_agent = agent
                     
                     break
                print(selected_agent.id_usuario) 
                
                # Encontrar los mejores matches y regresarlos con su puntaje, tambien usa conversaciones guardadas
                jupiter_instance2 = jupiter_class()

             
                top_matches_conversacion = jupiter_instance2.find_top_matches_conversation(selected_agent, agents)
                #encontrar los matches por compatibilidad
                top_matches_preferencia_pareja=jupiter_instance2.find_top_matches_preferencia_pareja(selected_agent,agents)

                top_matches_final=jupiter_instance2.find_top_matches_final(selected_agent.id_usuario,top_matches_preferencia_pareja,top_matches_conversacion)
                

                
                matched_agent_id1, match_score, preferencias1,conversation1 = top_matches_final.iloc[0] #top1
                matched_agent_id2, match_score, preferencias2,conversation2 = top_matches_final.iloc[1] #top2
                matched_agent_id3, match_score, preferencias3,conversation3 = top_matches_final.iloc[2] #top2
                
                # Encontrar el agente correspondiente
                matched_agent1 = next(agent for agent in agents if agent.id_usuario == matched_agent_id1)
                matched_agent2 = next(agent for agent in agents if agent.id_usuario == matched_agent_id2)
                matched_agent3 = next(agent for agent in agents if agent.id_usuario == matched_agent_id3)
                
                # Generar el resumen del match usando el LLM
                match_summary1 = jupiter_instance2.summarize_match_with_llm(selected_agent, matched_agent1, conversation1)
                match_summary2 = jupiter_instance2.summarize_match_with_llm(selected_agent, matched_agent2, conversation2)
                match_summary3 = jupiter_instance2.summarize_match_with_llm(selected_agent, matched_agent3, conversation3)
                
                preferencias1=formatear_preferencias(preferencias1)
                preferencias2=formatear_preferencias(preferencias2)
                preferencias3=formatear_preferencias(preferencias3) 
                          
                st.header("Potenciales Matches")
                # Primera sección para el primer usuario
                st.subheader(f"Primer usuario compatible: ¨{matched_agent1.id_usuario}¨")
                resumen_user_1 = st.text_area(f"Compatibilidad de perfiles {matched_agent1.id_usuario}", preferencias1, key="user_1",height=400)
                resumen_user_2 = st.text_area(f"Compatibilidad de interaccion {matched_agent1.id_usuario}", match_summary1, key="user_2",height=400)
                
                # Espaciado entre las secciones
                st.write("---")
                
                # Segunda sección para el segundo usuario
                st.subheader(f"Segundo usuario compatible: ¨{matched_agent2.id_usuario}¨")
                resumen_user_3 = st.text_area(f"Compatibilidad de perfiles {matched_agent2.id_usuario}", preferencias2, key="user_3",height=400)
                resumen_user_4 = st.text_area(f"Compatibilidad de interaccion {matched_agent2.id_usuario}", match_summary2, key="user_4",height=400)

                 # Espaciado entre las secciones
                st.write("---")
                
                # Tercera sección para el tercer usuario
                st.subheader(f"Tercer usuario compatible: ¨{matched_agent3.id_usuario}¨")
                resumen_user_5 = st.text_area(f"Compatibilidad de perfiles {matched_agent3.id_usuario}", preferencias3, key="user_5",height=400)
                resumen_user_6 = st.text_area(f"Compatibilidad de interaccion {matched_agent3.id_usuario}", match_summary3, key="user_6",height=400)
                
             #generar_resumen(st.session_state.usuario_seleccionado)
    
def proceso_chat():
    st.header("Chat pairing") 
    
    usuarios = cargar_usuarios_a_session_state()
    # Configuración de diseño con columnas
    col1, col2 = st.columns(2)
     
    with col1:
      usuario1 = st.selectbox("Selecciona el primer usuario:", usuarios, key="usuario1")
    # Menú desplegable en la segunda columna
    with col2:
      usuario2 = st.selectbox("Selecciona el segundo usuario:", usuarios, key="usuario2")
    
    inserter=MongoDBInserter() 
    matches = inserter.busca_matches(usuario1)

    #busca conversacion larga pairing
    conversacion=inserter.busca_conversacion_pairing(usuario1,usuario2)  
     
    #representa los display segun el caso si es match o no 
    if matches!=False:    
        if matches[0]==usuario2:
            print(f"{usuario2} es la primera opcion match de {usuario1} ")
            st.write(f"{usuario2} es la primera opcion match de {usuario1} :heart_on_fire:")
        elif matches[1]==usuario2:
            print(f"{usuario2} es la segunda opcion match de {usuario1} ")
            st.write(f"{usuario2} es la segunda opcion match de {usuario1} :heart_on_fire:")
            
        else:
            st.write(f"{usuario2} no es un match registrado para  {usuario1} :x:")    
    else:
       st.write(f"{usuario2} no es un match registrado para  {usuario1} :x:")

    
    if conversacion!=False:
     #busca conversacion para display ( tipo chat )
     conversacion_display=inserter.busca_conversacion_display_pairing(usuario1,usuario2)
     if conversacion_display!= False:
          #input(conversacion_display)
          lista_tuplas = [(item[0], item[1]) for item in conversacion_display]
          conversacion=(lista_tuplas,1)
          
     #input(type(conversacion))
     inserter.close_connection()
     #input(conversacion)
     usuario, texto = conversacion[0][0]
     #inserter=MongoDBInserter()   
     #genderuser1=inserter.busca_sexo(usuario)
     for mensaje in conversacion[0]:
        # Asegurarnos de que 'mensaje' sea una tupla o lista
        if isinstance(mensaje, tuple) and len(mensaje) == 2:
            usuario, texto = mensaje
            #genderuser1=inserter.busca_sexo(usuario)
            try:
             #avatar = f"./avatars/{usuario}.JPG"  
             avatar = os.path.join("avatars", f"{usuario}.jpg")  # Reemplaza usuario con el nombre apropiado
             if os.path.isfile(avatar):
                 pass
             else:
                 avatar = os.path.join("avatars", f"{usuario}.JPG")
                 if os.path.isfile(avatar):
                  pass
                 else:
                  avatar = "user"  # Avatar por defecto
            except Exception as e:
                  avatar = "user"  # Avatar por defecto      


            with st.chat_message("user",avatar=avatar):
                st.write(f"{usuario}: \n\n{texto.strip()}")
            time.sleep(0.5)

            
        else:
            print(f"Formato inesperado en mensaje: {mensaje}")  # Imprime para depuración

     inserter.close_connection()       
    

    
    
    

# Función principal
def app():
    # Título de la aplicación
    st.title("Aplicación de Matching de Usuarios :cupid:")
    
    with st.sidebar:
    # Barra lateral (Sidebar)
    # Imagen en la barra lateral
     st.sidebar.image("pairperu.png", width=290)

    # Menú lateral con opciones (usando streamlit-option-menu)
     menu = option_menu(
     menu_title='Menu',  # Título del menú
     options=['Redes Sociales','Preferencias' ,'Usuarios', 'Pairing','Chats'],  # Opciones del menú
     icons=['person-plus', 'people','people', 'heart','chat'],  # Iconos de las opciones
     menu_icon="list",  # Ícono del menú lateral
     default_index=0,  # Índice por defecto
     styles={  # Estilos personalizados
        "container": {"padding": "5!important", "background-color": "black"},  # Fondo del menú
        "icon": {"color": "#E91E63", "font-size": "23px"},  # Íconos en palo rosa
        "nav-link": {
            "color": "#F8BBD0",  # Texto en palo rosa claro
            "font-size": "20px",
            "text-align": "left",
            "margin": "0px",
            "--hover-color": "#F48FB1"  # Color al pasar el cursor (palo rosa intermedio)
        },
        "nav-link-selected": {"background-color": "#F06292"},  # Fondo de opción seleccionada (palo rosa suave)
    }
)
    # Lógica según la opción seleccionada
    if menu == "Redes Sociales":
        agregar_usuario()
    elif menu == "Usuarios":
        mostrar_usuarios()
    elif menu == "Pairing":
        proceso_pairing()
    elif menu == "Chats":
        proceso_chat()
    elif menu == "Preferencias":
        editar_preferencias()    
 

# Ejecutar la aplicación
if __name__ == "__main__":
    app()


