import os
from PIL import Image

class ComprimidorDeImagenes:
    def __init__(self, input_path, tamano_maximo_kb=150):
        """
        Inicializa el objeto de compresión de imágenes.
        
        :param input_path: Ruta de la imagen original
        :param tamano_maximo_kb: Tamaño máximo deseado en KB (por defecto 150 KB)
        """
        self.input_path = input_path
        self.tamano_maximo_kb = tamano_maximo_kb

    def comprimir(self):
        """
        Comprime la imagen ajustando la calidad para asegurarse de que el tamaño sea menor que el tamaño máximo deseado en KB.
        """
        # Abre la imagen original
        imagen = Image.open(self.input_path)

        # Verificar el tamaño original de la imagen
        tamano_actual = os.path.getsize(self.input_path) / 1024  # Tamaño en KB
        #print(f"Tamaño original de la imagen: {tamano_actual} KB")

        # Si la imagen original ya es más pequeña que el tamaño máximo deseado, no hace nada
        if tamano_actual <= self.tamano_maximo_kb:
           # print(f"La imagen ya es menor de {self.tamano_maximo_kb} KB.")
            return

        # Comienza con calidad 100 y reduce hasta que el tamaño sea menor al máximo permitido
        calidad = 100
        while calidad > 10:
            # Guarda la imagen con la calidad ajustada
            imagen.save(self.input_path, "JPEG", quality=calidad, optimize=True)

            # Verifica el tamaño de la imagen comprimida
            tamano_actual = os.path.getsize(self.input_path) / 1024  # Tamaño en KB
            #print(f"Tamaño actual de la imagen: {tamano_actual} KB (Calidad: {calidad})")

            # Si el tamaño es menor que el máximo, salir del bucle
            if tamano_actual < self.tamano_maximo_kb:
                #print(f"Imagen comprimida alcanzando un tamaño menor que {self.tamano_maximo_kb} KB.")
                break

            # Reducir la calidad para la siguiente iteración
            calidad -= 5  # Ajusta el decremento si es necesario

        if tamano_actual >= self.tamano_maximo_kb:
            #print(f"No se pudo reducir la imagen a menos de {self.tamano_maximo_kb} KB, el tamaño final es {tamano_actual} KB.")
            pass
        else:
            pass
            #print(f"Imagen comprimida y reemplazada: {self.input_path}")

def comprimir_imagenes_en_carpeta(image_folder, tamano_minimo_kb=1024, tamano_maximo_kb=150):
    """
    Comprime todas las imágenes en una carpeta que tengan un tamaño mayor al mínimo especificado (por defecto 1 MB) 
    y las reemplaza con las versiones comprimidas.
    
    :param image_folder: Carpeta que contiene las imágenes
    :param tamano_minimo_kb: Tamaño mínimo (en KB) de las imágenes a comprimir (por defecto 1024 KB = 1 MB)
    :param tamano_maximo_kb: Tamaño máximo deseado en KB (por defecto 150 KB)
    """
    # Cargar las imágenes de la carpeta
    image_files = [
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if f.lower().endswith(('png', 'jpg', 'jpeg'))
    ]

    # Comprimir cada imagen si su tamaño es mayor que el mínimo
    for image_file in image_files:
        # Obtener el tamaño de la imagen
        tamano_actual = os.path.getsize(image_file) / 500  # Tamaño en KB
        
        # Solo comprimir si el tamaño es mayor que 1 MB
        if tamano_actual > tamano_minimo_kb:
            # Crear una instancia de la clase y comprimir la imagen
            compresor = ComprimidorDeImagenes(image_file, tamano_maximo_kb)
            compresor.comprimir()
        else:
            pass
            #print(f"La imagen {image_file} ya tiene un tamaño menor o igual a 1 MB, no es necesario comprimirla.")



