from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

class DetectaNinos:
    def __init__(self, model_name="openai/clip-vit-base-patch32", threshold=0.9):
        """
        Inicializa el modelo CLIP y su procesador.

        :param model_name: Nombre del modelo preentrenado.
        :param threshold: Umbral para clasificar como True o False.
        """
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.threshold = threshold

    def is_photo_of_children(self, image):
        """
        Evalúa si una imagen es una foto de niños.

        :param image_path: Ruta a la imagen.
        :return: True si la probabilidad de los criterios es mayor al umbral, False de lo contrario.
        """
        # Cargar y procesar la imagen
        image = image.convert("RGB")
        
        # Definir los criterios de texto
        texts = [
            "a photo of a adult",        
            "a photo of a child",
        ]

        # Procesar entradas
        inputs = self.processor(text=texts, images=image, return_tensors="pt", padding=True)

        # Obtener logits y probabilidades
        outputs = self.model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        # Obtener las probabilidades de los primeros dos criterios
        probability_1 = probs[0, 0].item()  # Probabilidad para "a photo of a child abused"
        probability_2 = probs[0, 1].item()  # Probabilidad para "a photo of a pedophilia"
        
       
        # Verificar si cualquiera de los dos criterios supera el umbral
        return probability_2 > self.threshold
