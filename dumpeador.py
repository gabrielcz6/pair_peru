import json
from pymongo import MongoClient

# El documento que deseas insertar
documento = {
    "id_usuario": "angiesolari",
    "resumen": """Perfil de angiesolari

Conoce a angiesolari, una destacada abogada y consultora legal especializada en derecho empresarial. Su experiencia y dedicación le han permitido desarrollar un profundo conocimiento de las complejidades legales que enfrentan las empresas, reafirmando su compromiso con la excelencia profesional y el rigor jurídico.

Más allá de su carrera, angiesolari es una apasionada de la gastronomía y los momentos especiales. Es una entusiasta exploradora de restaurantes y cafeterías, siempre en busca de nuevos sabores y experiencias culinarias. Su amor por el sushi y la comida rápida demuestra su aprecio por la diversidad gastronómica.

En su tiempo libre, angiesolari cultiva hobbies que reflejan su curiosidad y creatividad. Disfruta de cocinar en casa, probando nuevas recetas, y de realizar viajes familiares llenos de aventura y aprendizaje. La creación de momentos inolvidables y el fortalecimiento de los lazos familiares son pilares fundamentales en su vida personal.

Sigue a angiesolari en Instagram (@solari.angie) para ser parte de su inspirador viaje, donde combina su pasión por el derecho, la gastronomía y los instantes que hacen de la vida una experiencia única."""
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