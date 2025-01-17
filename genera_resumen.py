import os,re
from datetime import datetime
# Descripción: Este script se encarga de generar un resumen de los datos obtenidos de los archivos de linkedin y de instagram

#funciones para linkedin
def obtener_educacion(file_path,ruta_linkedin):

    with open(f"{ruta_linkedin}/{file_path}", 'r', encoding="ISO-8859-1") as file:
        data = file.read()
       
    return data

def obtener_trabajo(file_path,ruta_linkedin):
    with open(f"{ruta_linkedin}/{file_path}", 'r', encoding="ISO-8859-1") as file:
        data = file.read()
        
    return data


#funciones para ig

def organizar_descripciones_y_hashtags(file_path,ruta_ig):
    # Leer el archivo .txt con los datos
    with open(f"{ruta_ig}/{file_path}", 'r', encoding='utf-8') as file:
        data = file.read()

    # Inicializar variables para almacenar las descripciones y hashtags
    descripciones = []
    hashtags = []

    # Dividir el contenido por cada sección encontrada (descripcion y hashtag)
    entries = data.split('\n________________________________________________________________\n')

    # Iterar sobre las entradas
    for entry in entries:
        # Separar la descripción de los hashtags
        lines = entry.split('\n')
        descripcion = ""
        entry_hashtags = []
        
        for line in lines:
            if line.startswith("descripcion:"):
                descripcion = line.replace("descripcion:", "").strip()
            elif line.startswith("hashtag:"):
                entry_hashtags.append(line.replace("hashtag:", "").strip())
        
        # Formatear la descripción y los hashtags
        if descripcion:
            descripciones.append(f" {descripcion}")
        if entry_hashtags:
            hashtags.append(f" {' '.join(entry_hashtags)}")

    # Unir todo en un solo string
    output_string = "\n\n"+"Descripciones y hashtags de las fotos: "+"\n\n"+"\n\n".join(descripciones) 
     #+"Hashtags de las fotos:" "\n\n" + "\n".join(hashtags)
    # Retornar el resultado
    return output_string

def obtener_descripcion(ruta_descripcion,ruta_ig):
    # Leer el contenido del archivo de descripción
    with open(f"{ruta_ig}/{ruta_descripcion}", 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Extraer la información de las líneas
    cantidad_post = lines[0].split(':')[1].strip()
    cantidad_seguidores = lines[1].split(':')[1].strip()
    cantidad_seguidos = lines[2].split(':')[1].strip()
    nombre = lines[3].split(':')[1].strip()
    descripcion = lines[4].split(':')[1].strip()

    # Crear el párrafo en formato string
    parrafo = (
        f"{nombre} tiene {cantidad_post} publicaciones en total. "
        f"Cuenta con {cantidad_seguidores} seguidores y sigue a {cantidad_seguidos} personas. "
        f"En su descripción se presenta como: {descripcion}."
    )
    
    return parrafo

def obtener_archivo_mas_reciente(archivos):
    # Filtrar los archivos que siguen el patrón "gabrielcz6_ddmmaaaa_instagram_posts_fotos"
    archivos_filtrados = archivos
        # Si la lista está vacía, devuelve None
    if not archivos_filtrados:
        return None

    # Devuelve el primer archivo de la lista
    return archivos[0]
    
    
def genera_resumen_ig(ruta_ig):
    # Ruta donde están los archivos
    ruta_ig = ruta_ig 
    # Obtener todos los archivos dentro de la carpeta
    archivos = os.listdir(ruta_ig)
    # Filtrar los archivos que siguen el patrón "gabrielcz6_ddmmaaaa_instagram_posts_fotos"
    archivos_fotos = [f for f in archivos if f.endswith('instagram_posts_fotos')]
    archivos_descripcion = [f for f in archivos if f.endswith('instagram_descripcion.txt')]
    archivos_posts = [f for f in archivos if f.endswith('instagram_posts.txt')]
    desripcion=obtener_descripcion(obtener_archivo_mas_reciente(archivos_descripcion),ruta_ig)
    #organi(obtener_archivo_mas_reciente(archivos_fotos))
    hashtagydescripcionpost=organizar_descripciones_y_hashtags(obtener_archivo_mas_reciente(archivos_posts),ruta_ig)
    rutafotos=f"{ruta_ig}\\{obtener_archivo_mas_reciente(archivos_fotos)}"
    return desripcion,hashtagydescripcionpost,rutafotos

def genera_resumen_linkedin(ruta_linkedin):
    # Ruta donde están los archivos
    ruta_linkedin = ruta_linkedin 
    # Obtener todos los archivos dentro de la carpeta
    archivos = os.listdir(ruta_linkedin)
    # Filtrar los archivos que siguen el patrón "gabrielcz6_ddmmaaaa_instagram_posts_fotos"
    
    archivos_educacion = [f for f in archivos if f.endswith('educacion.txt')]
    archivos_trabajo = [f for f in archivos if f.endswith('trabajo.txt')]

    educacion=obtener_educacion(obtener_archivo_mas_reciente(archivos_educacion),ruta_linkedin)
    trabajo=obtener_trabajo(obtener_archivo_mas_reciente(archivos_trabajo),ruta_linkedin)

    return educacion,trabajo



