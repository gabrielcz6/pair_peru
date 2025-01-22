import streamlit as st
from perfilanalyzer import PerfilAnalyzer
import time
import pandas as pd
from utils.db_connection.mongodb import MongoDBInserter
from utils.jupiter import jupiter_class, GPTAgent
from streamlit_option_menu import option_menu



# Función de ejemplo para generar un resumen
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



#DEL MENU PRINCIPAL

# Función para agregar un nuevo usuario
def agregar_usuario():
    st.header("Agregar nuevo usuario")
    
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
        inserter = MongoDBInserter()
        users = inserter.get_all_users()
        df_usuarios = pd.DataFrame(users)

        # Guardar en session_state
        st.session_state.df_usuarios = df_usuarios[[
            "id_usuario", "ig_user", "linkedin_user", "genero", "trabajo", "estudio", "hobbies", "lugares", "comidas"
        ]]

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
    inserter = MongoDBInserter()
    profiles = inserter.get_all_users()
    df_usuarios = pd.DataFrame(profiles)

        # Guardar en session_state
    st.session_state.df_usuarios = df_usuarios[[
            "id_usuario", "ig_user", "linkedin_user", "genero", "trabajo", "estudio", "hobbies", "lugares", "comidas"
        ]]
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

                # Encontrar los mejores matches
                jupiter_instance2 = jupiter_class()
                top_matches = jupiter_instance2.find_top_matches(selected_agent, agents)
                ## Crear una tabla con os resultados del score
                df_matches = pd.DataFrame(columns=['perfil','score'])
                i = 0
                for match in top_matches:
                    df_matches.loc[i] = (match[0],match[1])
                    i = i + 1
                print(df_matches)
                ## Crear un resumen del match
                # Obtener el mejor match
                best_match1 = top_matches[0]  # El primer elemento es el mejor match
                best_match2 = top_matches[1]  # El segundo elemento es el segundo mejor match
                matched_agent_id1, match_score, conversation1 = best_match1
                matched_agent_id2, match_score, conversation2 = best_match2
                
                # Encontrar el agente correspondiente
                matched_agent1 = next(agent for agent in agents if agent.id_usuario == matched_agent_id1)
                matched_agent2 = next(agent for agent in agents if agent.id_usuario == matched_agent_id2)
                
                # Generar el resumen del match usando el LLM
                match_summary1 = jupiter_instance2.summarize_match_with_llm(selected_agent, matched_agent1, conversation1)
                match_summary2 = jupiter_instance2.summarize_match_with_llm(selected_agent, matched_agent2, conversation2)

          
                st.header("Potenciales Matches")
                # Primera sección para el primer usuario
                st.subheader(f"Usuario: ¨{matched_agent1.id_usuario}¨")
                resumen_user_1 = st.text_area(f"Resumen de Justificación para {matched_agent1.id_usuario}", match_summary1, key="user_1",height=400)
                
                # Espaciado entre las secciones
                st.write("---")
                
                # Segunda sección para el segundo usuario
                st.subheader(f"Usuario: ¨{matched_agent2.id_usuario}¨")
                resumen_user_2 = st.text_area(f"Resumen de Justificación para {matched_agent2.id_usuario}", match_summary2, key="user_2",height=400)
                
             #generar_resumen(st.session_state.usuario_seleccionado)
    

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
     options=['Agregar usuario', 'Usuarios', 'Pairing'],  # Opciones del menú
     icons=['person-plus', 'people', 'heart'],  # Iconos de las opciones
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
    if menu == "Agregar usuario":
        agregar_usuario()
    elif menu == "Usuarios":
        mostrar_usuarios()
    elif menu == "Pairing":
        proceso_pairing()


# Ejecutar la aplicación
if __name__ == "__main__":
    app()


