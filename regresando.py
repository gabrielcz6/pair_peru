import json

# Definir la ruta del archivo
file_path = 'resumenes_perfil/gabrielcz6_perfil_ig.txt'

# Leer el contenido del archivo
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = file.read()
# Convertir el texto leído a un objeto Python (diccionario o lista según el contenido)
data = json.loads(json_data)

# Mostrar el resultado
print(data["trabajo"])