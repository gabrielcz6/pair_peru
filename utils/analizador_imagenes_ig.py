import os
from PIL import Image
import google.generativeai as genai
from utils.filtro_ninos import DetectaNinos
from utils.comprime_imagenes import ComprimidorDeImagenes
import random
import time

class Instagram_Image_Analyzer:
    def __init__(self, api_key):
        """
        Inicializa el modelo generativo con la clave API proporcionada.
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    def analyze_account(self, image_folder):
        """
        Analiza una carpeta de imágenes y una descripción para generar un JSON con tipos de comidas, lugares y hobbies.

        Args:
            image_folder (str): Ruta a la carpeta que contiene las imágenes.
            descriptions (str): Texto descriptivo relacionado con las imágenes.

        Returns:
            dict: Respuesta generada en formato JSON.
        """
        # Verificar que la carpeta exista
        if not os.path.isdir(image_folder):
            raise FileNotFoundError(f"La carpeta '{image_folder}' no existe.")

        # Cargar las imágenes de la carpeta
        image_files = [
            os.path.join(image_folder, f)
            for f in os.listdir(image_folder)
            if f.lower().endswith(('png', 'jpg', 'jpeg'))
        ]
          # Comprimir cada imagen si su tamaño es mayor que el mínimo
          # Comprimir cada imagen si su tamaño es mayor que el mínimo
        for image_file in image_files:
            # Obtener el tamaño de la imagen
            tamano_actual = os.path.getsize(image_file) / 1024  # Tamaño en KB
            
            # Solo comprimir si el tamaño es mayor que 1 MB
            if tamano_actual > 150:
                # Crear una instancia de la clase y comprimir la imagen
                compresor = ComprimidorDeImagenes(image_file, 150)
                compresor.comprimir()
            else:
                pass
                #print(f"La imagen {image_file} ya tiene un tamaño menor o igual a 1 MB, no es necesario comprimirla.")
             
    



        analiza_ninos=DetectaNinos()
        if not image_files:
            raise ValueError("No se encontraron imágenes en la carpeta proporcionada.")

                # Filtrar imágenes que no sean fotos de niños
        filtered_images = [Image.open(image_file) for image_file in image_files 
                           if not analiza_ninos.is_photo_of_children(Image.open(image_file))]
        
        # Validar si hay más de 100 imágenes
        if len(filtered_images) > 100:
            # Seleccionar 100 imágenes aleatorias
            filtered_images = random.sample(filtered_images, 100)

        # Prompt para el modelo
        prompt = """
        Te voy a pasar las fotos y descripciones de una cuenta de redes sociales de una persona. En base a las fotos, genera una lista de tipos de lugares que le gusta a esta persona, como por ejemplo: playa, ciudades, campo, desiertos, entre otros.
        La salida solo deberá ser en formato JSON, claro y limpio, con la siguiente estructura:
        {
            "comidas": ["Genera una lista de tipos de comida, como ensaladas, comida rápida, comida italiana, entre otros. maximo 2 palabras."],
            "lugares": ["Genera una lista de lugares relacionados con la comida, como restaurantes, cafeterías, food trucks, etc. maximo 2 palabras."],
            "hobbies": ["Genera una lista de hobbies relacionados con la comida, como cocinar, explorar restaurantes, aprender recetas, entre otros. maximo 2 palabras."]
        }
        """

        # Generar contenido utilizando el modelo
        try:
            response = self.model.generate_content([prompt] + filtered_images) 

        except:
            "aca elegimos aleatoriamente las fotos"

        return response.text