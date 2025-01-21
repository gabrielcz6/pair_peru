from instagram_scraping import pair_scraping_Instagram
from linkedin_scraping import pair_linkedin_scraping
from genera_resumen import genera_resumen_ig, genera_resumen_linkedin
from utils.gpt import InstagramandlinkedinAnalyzer
from utils.analizador_imagenes_ig import Instagram_Image_Analyzer
from dotenv import load_dotenv
import os
import shutil
import json
from utils.db_connection.mongodb import MongoDBInserter
from utils.parse_combine_json import parse_json_from_string, combinar_datos

class PerfilAnalyzer:
    def __init__(self, ig_username, linkedin_username,genero,id_usuario):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()

        # Acceder a las claves
        self.api_key = os.getenv("API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        self.id_usuario=id_usuario
        self.genero=genero
        self.ig_username = ig_username
        self.linkedin_username = linkedin_username

    def analizar_perfil(self):
        # Realizar el scraping de Instagram y LinkedIn
        ruta_ig = pair_scraping_Instagram(self.ig_username)
        ruta_linkedin = pair_linkedin_scraping(self.linkedin_username)
        #ruta_ig="oavellaneda_perfil_ig"
        #ruta_linkedin="omar-avellaneda-cfa-cesga-64694734_perfil_linkedin"

        # Generar resumen de LinkedIn
        resumen_linkedin = genera_resumen_linkedin(ruta_linkedin)
        analyzer_linkedin = InstagramandlinkedinAnalyzer(self.api_key)
        
        # Función que analiza trabajo en LinkedIn
        result_linkedin_trabajo = analyzer_linkedin.analyze_linkedin_trabajo(resumen_linkedin)
        
        # Función que analiza estudios en LinkedIn
        result_linkedin_estudio = analyzer_linkedin.analyze_linkedin_estudio(resumen_linkedin)

        # Generar resumen de Instagram
        ig_descripcion, ig_hashtagfotos, ruta_ig_fotos = genera_resumen_ig(ruta_ig)

        # Analizador de imágenes de Instagram basado en Gemini
        analyzer_fotos = Instagram_Image_Analyzer(api_key=self.google_api_key)

        resultado_ig_fotos = analyzer_fotos.analyze_account(ruta_ig_fotos)

        # Clase para análisis de texto de Instagram y LinkedIn basado en GPT
        analyzer_ig_text = InstagramandlinkedinAnalyzer(self.api_key)

        # Función que analiza todo el texto de las fotos y hashtags en Instagram
        result_ig_lugares_comida_hobbie = analyzer_ig_text.analyze_ig_lugares_comida_hobbies(ig_hashtagfotos)

        # Parsear los strings obtenidos
        result_linkedin_trabajo = parse_json_from_string(result_linkedin_trabajo)
        result_linkedin_estudio = parse_json_from_string(result_linkedin_estudio)
        result_ig_lugares_comida_hobbie = parse_json_from_string(result_ig_lugares_comida_hobbie)
        resultado_ig_fotos = parse_json_from_string(resultado_ig_fotos)

        # Combinar todos los resultados
        jsonfinal = combinar_datos(result_linkedin_trabajo, result_linkedin_estudio, result_ig_lugares_comida_hobbie, resultado_ig_fotos)
        
         # Guardar el resultado en un archivo .txt
        file_path = f'resumenes_perfil/{self.ig_username}.txt'
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(jsonfinal)
    
        try:
         #guardarlo en mongodb
          jsonfinal = json.loads(jsonfinal)
          jsonfinal["ig_user"] = self.ig_username
          jsonfinal["linkedin_user"] = self.linkedin_username
          jsonfinal["id_usuario"] = self.id_usuario
          jsonfinal["genero"] = self.genero

         # input(type(jsonfinal))
         # Crear una instancia de la clase y insertar los datos
          inserter = MongoDBInserter("profilesdatabase", "profiles")
          inserter.insert_data(jsonfinal)
          
          try:
           # Eliminar las carpetas y su contenido
           shutil.rmtree(ruta_ig)
           shutil.rmtree(ruta_linkedin)
          except:
             "no se pudo eliminar las carpetas"

        except Exception as e:
           print (str(e))

        return file_path


    def guardar_perfil_db(self,documento):
        
       # Crear instancia del administrador de MongoDB
       manager = MongoDBInserter() 
       document_id = manager.insert_data(documento)
       print(f"El documento fue insertado con éxito. ID: {document_id}")