from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time,os
import undetected_chromedriver as uc
from datetime import datetime


def linkedin_scraping(username):
   
   
   options = uc.ChromeOptions()
   options.add_argument("--headless")  
   options.add_argument("--force-device-scale-factor=0.5")
   driver = uc.Chrome(options=options)
   
   fecha=datetime.now().strftime("%d%m%Y")
   
   driver.get("https://www.linkedin.com/")
   

   time.sleep(4)

   WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'login')]"))).click() 
   time.sleep(2)
   WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("gabrielcanepamercado@gmail.com") 
   time.sleep(2)
   WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.ID, "password"))).send_keys("Pairperu2025..") 
   time.sleep(2)
   WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']"))).click()
   
   
   driver.get(f"https://www.linkedin.com/in/{username}/")
   
   time.sleep(4)
   #-----------------------------------------------------------------------
   #usuario para scrapear
   time.sleep(5)
   # Crear carpeta específica para el perfil
   folder_name = f"{username}_perfil_linkedin"
   if not os.path.exists(folder_name):
       os.makedirs(folder_name)


   #
   """
   try:
       driver.find_element(By.ID, "navigation-index-see-all-experiences").click()
       time.sleep(5)
       a = driver.find_elements(By.XPATH, "//section[.//h1[text()='Experience']]//div[contains(@class, 'display-flex') and contains(@class, 'align-items-center') and contains(@class, 'mr1') and contains(@class, 't-bold')]//span[1]")

   except:
       a = driver.find_elements(By.XPATH, "//section[.//div[@id='experience']]//div[contains(@class, 'display-flex') and contains(@class, 'align-items-center')and contains(@class, 'mr1') and contains(@class, 't-bold')]//span[1]")
       pass
    """     
   a = driver.find_elements(By.XPATH, "//section[.//div[@id='experience']]//div[contains(@class, 'display-flex') and contains(@class, 'align-items-center')and contains(@class, 'mr1') and contains(@class, 't-bold')]//span[1]")  
   
   b = driver.find_elements(By.XPATH, "//section[.//div[@id='experience']]//div[contains(@class, 'display-flex')"     
               "and contains(@class, 'flex-column') "
               "and contains(@class, 'full-width')]"
               "/span[contains(@class, 't-14') "
               "and contains(@class, 't-normal')][1]"
               "/span")   
   
       # List to store unique elements
   unique_b = []
   
   # Bucle para recorrer los elementos de 'b'
   for element in b:
       # Verificamos si el texto ya está en la lista de elementos únicos
       if element.text not in [e.text for e in unique_b]:
           # Si no está repetido, lo agregamos a la lista 'unique_b'
           unique_b.append(element)      
   

   # Ahora 'unique_b' contiene solo los elementos con textos únicos
     # Y puedes continuar con el proceso que tenías para escribir en el archivo
   with open(f"{folder_name}/{username}_{fecha}_trabajo.txt", "w") as file:
         # Iteramos las listas alternadamente
         for i in range(max(len(a), len(unique_b))):  # Iterar hasta el tamaño máximo de las listas
             if i < len(a):  # Si aún hay elementos en 'a'
                 file.write(a[i].text + "\n")
             if i < len(unique_b):  # Si aún hay elementos en 'b' sin duplicados
                 file.write(unique_b[i].text + "\n")
             file.write("-------------\n")    




   driver.get(f"https://www.linkedin.com/in/{username}/")
     
   time.sleep(5)
   try: 
     a = driver.find_elements(By.XPATH, "//section[.//div[@id='education']]//div[contains(@class, 'display-flex') and contains(@class, 'align-items-center')and contains(@class, 'mr1') and contains(@class, 't-bold')]//span[1]")   
     
     b = driver.find_elements(By.XPATH, "//section[.//div[@id='education']]//a[contains(@class, 'optional-action-target-wrapper') "
               "and contains(@class, 'display-flex') "
               "and contains(@class, 'flex-column') "
               "and contains(@class, 'full-width')]"
               "/span[contains(@class, 't-14') "
               "and contains(@class, 't-normal')][1]"
               "/span")   
  
        # List to store unique elements
     unique_b = []
     
     # Bucle para recorrer los elementos de 'b'
     for element in b:
         # Verificamos si el texto ya está en la lista de elementos únicos
         if element.text not in [e.text for e in unique_b]:
             # Si no está repetido, lo agregamos a la lista 'unique_b'
             unique_b.append(element)
     
     # Ahora 'unique_b' contiene solo los elementos con textos únicos
     # Y puedes continuar con el proceso que tenías para escribir en el archivo
     with open(f"{folder_name}/{username}_{fecha}_educacion.txt", "w") as file:
         # Iteramos las listas alternadamente
         for i in range(max(len(a), len(unique_b))):  # Iterar hasta el tamaño máximo de las listas
             if i < len(a):  # Si aún hay elementos en 'a'
                 file.write(a[i].text + "\n")
             if i < len(unique_b):  # Si aún hay elementos en 'b' sin duplicados
                 file.write(unique_b[i].text + "\n")
             file.write("-------------\n")    
         
         # Agregar la línea separadora
         
   except Exception as e: 
      print("error: " + str(e))

   try:
       driver.close()
       time.sleep(10)
   except Exception as e:  
         print("error: " + str(e))
         
   
