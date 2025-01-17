# Importamos las librerías necesarias
import google.generativeai as genai
import PIL.Image
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

GOOGLE_API_KEY=''
genai.configure(api_key=GOOGLE_API_KEY)

# Configuración para caracteres especiales en la terminal de Python


# Configuramos el modelo
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Ruta a la carpeta que contiene las imágenes
image_folder = "gabrielcz6_perfil_ig\\gabrielcz6_13012025_instagram_posts_fotos"  # Cambia esto a la ruta de tu carpeta con las fotos
image_folder="carlos.gl87_perfil_ig\\carlos.gl87_11012025_instagram_posts_fotos"
# Cargar todas las imágenes de la carpeta
descripciones="descripciones"
image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

# Crear una lista de imágenes usando PIL
images = [PIL.Image.open(image_file) for image_file in image_files]

# Prompt para el modelo
prompt = """
Te voy a pasar las fotos y descripciones de una cuenta de Instagram de una persona, en base a las fotos genera una lista de tipos de lugares que le gusta a esta persona, como por ejemplo: playa, ciudades, campo, desiertos, entre otros.
 La salida solo deberá ser en formato JSON, claro y limpio, con la siguiente estructura:
    {{
        "comidas": [{{"Genera una lista de tipos de comida, como ensaladas, comida rápida, comida italiana, entre otros."}}],
         "lugares": [{{""Genera una lista de lugares relacionados con la comida, como restaurantes, cafeterías, food trucks, etc."}}],
          "hobbies": [{{Genera una lista de hobbies relacionados con la comida, como cocinar, explorar restaurantes, aprender recetas, entre otros."}}],
        
    }}
"""

# Generar contenido utilizando las imágenes
response = model.generate_content([prompt] + images + descripciones)

# Imprimir la respuesta del modelo
print(response.text)


 
