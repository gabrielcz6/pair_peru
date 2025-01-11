import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os
from datetime import datetime
from urllib.parse import unquote
import wget
from random import randint



def crearchromedriver():
      #---------------------------iniciar chrome driver-----------------------
   chrome_options = ChromeOptions()
   chrome_options.add_argument("--start-maximized")  # Maximiza la ventana del navegador
   chrome_options.add_argument('--headless')  # Activa el modo headless o invisible
   #chrome_options.add_argument('--disable-gpu')  # Desactiva la GPU para ahorrar recursos
   driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
   driver.set_window_position(0, 0)
   #-----------------------------------------------------------------------
   #usuario para scrapear
   return driver

def extraercomentariosyhashtageimagen(driver,iguserid,folder_name):
   folder_name=folder_name
   date=datetime.now().strftime("%d%m%Y")
   try:
    
    #-------------------extraer comentarios y hashtag-------------------------------

    with open(f"{folder_name}/{iguserid}_{date}_instagram_posts.txt", "a", encoding="utf-8") as file:
        # Buscar el contenedor con el XPath dado
        contenedor = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div[2]/div[1]/article/div/div[2]")
        
        # Buscar todos los `div` con `role="button"` dentro del contenedor
        botones = contenedor.find_elements(By.XPATH, './/div[@role="button"]')
        
        for boton in botones:
            # Buscar un `<a>` con texto "username" dentro del `div`
            enlace = boton.find_elements(By.XPATH, f".//a[text()='{iguserid}']")
            
            if enlace:
                # Escribir en el archivo que se encontró el enlace
                file.write(f"Encontrado una descripcion y hashtags '{iguserid}'\n")
                
                # Buscar un `<h1>` dentro del mismo `div`
                h1_element = boton.find_elements(By.XPATH, './/h1')
                if h1_element:
                    # Extraer el texto del `<h1>` y guardar en el archivo
                    h1_texto = h1_element[0].text
                    file.write(f"descripcion: {h1_texto}\n")
                    
                    # Buscar todos los `<a>` dentro del `<h1>` y extraer su texto
                    enlaces_dentro_h1 = h1_element[0].find_elements(By.XPATH, './/a')
                    for a in enlaces_dentro_h1:
                        file.write(f"hashtag: {a.text}\n")
                # Agregar línea de separación
                file.write("________________________________________________________________\n")   
    
     #-------------------extraer fotos x cada link-------------------------------  
   
    carpeta=f"{folder_name}/{iguserid}_{date}_instagram_posts_fotos" 
    if not os.path.exists(f"{folder_name}/{iguserid}_{date}_instagram_posts_fotos"):
        os.makedirs(f"{folder_name}/{iguserid}_{date}_instagram_posts_fotos")

    try:
       # Encontrar el contenedor específico utilizando el XPath proporcionado
       container_element = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div[2]/div[1]/article/div/div[1]")
   
       # Buscar todas las imágenes dentro de este contenedor
       img_elements = container_element.find_elements(By.TAG_NAME, 'img')
   
       # Verificar si se encontraron imágenes
       if img_elements:
        time.sleep(randint(1, 5))
        # Obtener la lista de archivos en la carpeta
        existing_files = os.listdir(carpeta)
    
        # Filtrar los archivos que siguen el patrón 'usernameNN.jpg' (donde NN es un número)
        existing_numbers = []
        for file in existing_files:
            if file.startswith(iguserid) and file.endswith('.jpg'):
                # Extraer el número de la imagen
                try:
                    number = int(file[len(iguserid):-4])  # Extraer número entre username y '.jpg'
                    existing_numbers.append(number)
                except ValueError:
                    pass  # Ignorar si no se puede convertir a número
    
        # Obtener el siguiente número disponible (si no hay archivos existentes, empezar en 1)
        next_number = max(existing_numbers, default=0) + 1
    
        # Iterar sobre los elementos de imagen encontrados
        for img_element in img_elements:
            try:
                # Obtener el valor del atributo `src`
                src_original = img_element.get_attribute("src")
    
                # Limpiar la URL utilizando `unquote`
                url_limpia = unquote(src_original)
    
                # Verificar si el archivo ya existe
                while True:
                    save_as = os.path.join(carpeta, f"{iguserid}_{date}_instagram_foto_{next_number}.jpg")
                    if not os.path.exists(save_as):
                        break
                    next_number += 1
    
                # Descargar la imagen
                wget.download(url_limpia, save_as)
    
                print(f"Imagen guardada correctamente: {save_as}")
    
                # Incrementar el número para el siguiente archivo
                next_number += 1
    
            except Exception as e:
                print(f"Error guardando la foto: {e}")
       else:
           print("No se encontraron imágenes en la página.")
       
    except Exception as e:
        print(f"Error: {e}")

   
    
   except Exception as e:
       print(f"Error: {e}")

def Scrape_1(iguserid,date,driver):
   print("scrape 1")
   driver.get("https://www.instagram.com/")
   time.sleep(2)
   
   #login
   try:           
    WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("pair.peru")
    WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys("Pairperu2025..")
    WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form//button[@type="submit"]'))).click()  
   except Exception as e:
    print("Error en el login: ", e)
   time.sleep(7)

   #busca datos
   try:           
    driver.get(f"https://www.instagram.com/{iguserid}") 
    time.sleep(2)
   except Exception as e:
    print("Error al intentar el scrapping", e)

   #cuantos post
   try:                                                                                  
      cantpost=      WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[1]/div/span/span'))).text  
      cantseguidores=WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a/span/span'))).text  
      cantseguidos=  WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[3]/div/a/span/span'))).text  
      nombre=        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[4]/div/div[1]/span'))).text  
      descripcion=   WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[4]/div/span/div/span'))).text
   except Exception as e:
    descripcion=""
    print("Error: ", e)

   # Crear carpeta específica para el perfil
   folder_name = f"{iguserid}_perfil_ig"
   if not os.path.exists(folder_name):
       os.makedirs(folder_name)
#scrapear todos los links de cada publicacion
   try:
      # Hacer scroll hacia abajo hasta el final de la página
      for i in range(int(cantpost)//2):

         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
         time.sleep(1)

         links = driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div//a")
         
         #Guardar los enlaces en un archivo txt
         try:
           for link in links:
             href = link.get_attribute('href')
             if href:  # Verifica que el enlace no sea None
                 # Leer los enlaces existentes desde el archivo
                 try:
                     with open(f"{folder_name}/{iguserid}_{date}_instagram_links.txt", "r") as file:
                         enlaces_existentes = set(file.read().splitlines())
                 except FileNotFoundError:
                     enlaces_existentes = set()  # Si no existe el archivo, iniciamos con un conjunto vacío
     
                 # Verificar si el enlace ya está en el archivo
                 if href not in enlaces_existentes:
                     with open(f"{folder_name}/{iguserid}_{date}_instagram_links.txt", "a") as file:
                         file.write(href + "\n")  # Agregar el enlace al archivo
         except Exception as e:
              print("Error: ", e)      

         #guardando la descrpicion del perfil
         with open(f"{folder_name}/{iguserid}_{date}_instagram_descripcion.txt", "w", encoding="utf-8") as archivo:
          archivo.write(f"cantidad de post: {cantpost}\n")
          archivo.write(f"cantidad de seguidores: {cantseguidores}\n")
          archivo.write(f"cantidad de seguidos: {cantseguidos}\n")
          archivo.write(f"nombre: {nombre}\n")
          archivo.write(f"descripcion : {descripcion}\n")              
          
   except Exception as e:
    print("Error: ", e)
   
   return cantpost,cantseguidores,cantseguidos,nombre,descripcion 

def Scrape_2(iguserid,date,driver):

   folder_name = f"{iguserid}_perfil_ig"

   # Encuentra todos los elementos <a> dentro del XPath que proporcionaste
   
      # Leer los enlaces del archivo txt
   try:
       with open(f"{folder_name}/{iguserid}_{date}_instagram_links.txt", "r") as file:
           enlaces = file.read().splitlines()  # Lista de enlaces
   except FileNotFoundError:
       print("El archivo 'links.txt' no existe. Asegúrate de haber generado el archivo.")
       enlaces = []
   
   # Verificar si hay enlaces para procesar
   if enlaces:
       
       print("Entrando a cada enlace para extraer fotos y hashtags ...")

       for enlace in enlaces:
           try:
               
               driver.get(enlace)  # Navegar al enlace
               print(f"Visitando: {enlace}")
               time.sleep(3)  # Esperar un tiempo para cargar la página
               #llamando la otra funcion usando el driver
               extraercomentariosyhashtageimagen(driver,iguserid,folder_name)
               #input("pausita")

           except Exception as e:
               print(f"Error al intentar visitar {enlace}: {e}")
   else:
       print("No hay enlaces en 'links.txt' para procesar.") 

def pair_scraping_Instagram(iguserid):
   
   date=datetime.now().strftime("%d%m%Y")

   driver=crearchromedriver() 

   Scrape_1(iguserid,date,driver)
   Scrape_2(iguserid,date,driver)

   print("extraidos los detalles y fotos")

   driver.quit()
   
