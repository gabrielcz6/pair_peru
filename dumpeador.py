import json
from pymongo import MongoClient

# El documento que deseas insertar
documento ={
    "trabajo": [
        "analista de clima y cultura",
        "asistente de gestion de talento",
        "psicologo organizacional",
        "practicante de gestion humana",
        "practicante universitaria"
    ],
    "estudio": {
        "carrera": "psicologia",
        "especialidad": "psicologia organizacional"
    },
    "lugares": [
        "pastelerias",
        "cafeterias"
    ],
    "comidas": [
        "dulces",
        "pasteles"
    ],
    "hobbies": [
        "reposteria",
        "hornear",
        "estudio",
        "viajes",
        "deportes",
        "fotografia",
        "artes"
    ],
    "ig_user":"luisamazeyra",
    "linkedin_user":"luisa-mazeyra-zuñiga-834835141",
}
# Conectar a MongoDB (asegúrate de que MongoDB esté corriendo en el puerto 27017)
client = MongoClient('mongodb+srv://gabrielcanepamercado:JOJ1X0FwJrcl6gCl@cluster0.hppcb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

# Seleccionar la base de datos y colección
db = client["profilesdatabase"]  # Cambia el nombre de la base de datos si lo deseas
collection = db["profiles"]  # Cambia el nombre de la colección si lo deseas

# Insertar el documento en la colección
resultado = collection.insert_one(documento)

# Imprimir el ID del documento insertado
print(f"Documento insertado con ID: {resultado.inserted_id}")