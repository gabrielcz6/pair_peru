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
from dotenv import load_dotenv
from random import randint


def crearchromedriver():
      #---------------------------iniciar chrome driver-----------------------
   chrome_options = ChromeOptions()
   chrome_options.add_argument("--start-maximized")  # Maximiza la ventana del navegador
   chrome_options.add_argument("--force-device-scale-factor=0.5")
   #chrome_options.add_argument('--headless')  # Activa el modo headless o invisible
   #chrome_options.add_argument('--disable-gpu')  # Desactiva la GPU para ahorrar recursos
   driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
   driver.set_window_position(0, 0)
   #-----------------------------------------------------------------------
   #usuario para scrapear
   return driver


def Scrape_1(fblink,date,driver):
   load_dotenv()

   # Obtener credenciales
   username = os.getenv("USERNAME_IG")
   password = os.getenv("PASSWORD_IG")

   print("scrape 1")
   driver.get("https://www.facebook.com/")
   time.sleep(4)

#login
   try:           
    username="katyrcatui@gmail.com"
    password="Pairperu2025.."

    WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(username)
    WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.NAME, "pass"))).send_keys(password)
    WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.NAME, "login"))).click()  
    
    time.sleep(6)
    driver.get("{fblink}&sk=photos_albums")

    #crear carpeta para guardar lo scraperado de facebook
    # # Crear carpeta específica para el perfil
    folder_name = f"{userid}_perfil_facebook"
    if not os.path.exists(folder_name):
          os.makedirs(folder_name)    


    input("cats")
   except Exception as e:
    print("Error en el login: ", e)



userid="gabrielcanepa"
date=datetime.now().strftime(f"%d%m%Y")
driver=crearchromedriver()
Scrape_1("https://www.facebook.com/profile.php?id=100034171332484",date,driver,userid)