import json
from pymongo import MongoClient

# El documento que deseas insertar
documento = {
    "id_user_agent1": "angiesolari",
    "id_user_agent2": "gabrielcanepa",
    "conversation": "",
"score":"6"
}
# Conectar a MongoDB (asegúrate de que MongoDB esté corriendo en el puerto 27017)
client = MongoClient('mongodb+srv://gabrielcanepamercado:JOJ1X0FwJrcl6gCl@cluster0.hppcb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

# Seleccionar la base de datos y colección
db = client["profilesdatabase"]  # Cambia el nombre de la base de datos si lo deseas
collection = db["summary_profiles"]  # Cambia el nombre de la colección si lo deseas

# Insertar el documento en la colección
resultado = collection.insert_one(documento)

# Imprimir el ID del documento insertado
print(f"Documento insertado con ID: {resultado.inserted_id}")