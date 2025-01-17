import json
from pymongo import MongoClient

# Conectar a MongoDB (asegúrate de que MongoDB esté corriendo en el puerto 27017)
client = MongoClient('mongodb+srv://gabrielcanepamercado:JOJ1X0FwJrcl6gCl@cluster0.hppcb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

# Seleccionar la base de datos y colección
db = client["profilesdatabase"]  # Cambia el nombre de la base de datos si lo deseas
collection = db["profiles"]  # Cambia el nombre de la colección si lo deseas

# Obtener todos los documentos de la colección
documentos = collection.find()

# Guardar cada documento en un archivo .txt
for i, documento in enumerate(documentos, 1):
    # Convertir el documento a formato JSON (por si contiene objetos)
    documento_json = json.dumps(documento, default=str, indent=4)
    
    # Crear un archivo txt para cada documento
    with open(f"documento_{i}.txt", "w") as file:
        file.write(documento_json)

    print(f"Documento {i} guardado como documento_{i}.txt")
