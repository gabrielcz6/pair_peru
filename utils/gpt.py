import os
import json
import uuid
import time
import re
import openai
import shutil
from tqdm import tqdm
from datetime import datetime
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.output_parsers import StrOutputParser


class InstagramandlinkedinAnalyzer:
    def __init__(self, api_key,model_name="gpt-4o"):
        """
        Initializes the InstagramAnalyzer class with the given API key and model name.

        :param api_key: The API key for the language model.
        :param model_name: The model name to use (default is "gpt-4o").
        """
        self.llm = ChatOpenAI(model_name=model_name, api_key=api_key)
         
         
        self.prompt_template_linkedin_trabajo= PromptTemplate(
    input_variables=["texto"],
    template="""
   Te voy a pasar los trabajos y los estudios de una persona de su cuenta de LinkedIn, en base a esto devuelve un solo un formato json  .
    {{
         "tipostrabajo":[{{" tipos de trabajo que ha tenido esta persona, por ejemplo: ingenieros de software, ux specialist, growth hacker, entre otros "}}],
        
    }}

    texto :     {texto}
    """

)   

        self.prompt_template_linkedin_estudio= PromptTemplate(
    input_variables=["texto"],
    template="""
   Te voy a pasar los trabajos y los estudios de una persona de su cuenta de LinkedIn, en base a esto simplifica a que carrera pertenece esta persona y su especialidad, como por ejemplo: médico, pediatra
    {{
        "carrera":"carrera general a la que pertenece",
        "especialidad":"especialidad de la carrera a la que pertenece",
        
    }}

    texto :     {texto}
    """

)        


        self.prompt_template_ig_comidas = PromptTemplate(
    input_variables=["texto"],
    template="""
    Te voy a pasar las descripciones de fotos y los hashtags de una cuenta de Instagram de una persona, en base a las descripciones de fotos y el texto genera una lista de tipos de comidas que le gusta a esta persona.
    La salida solo deberá ser en formato JSON, claro y limpio, con la siguiente estructura:
    {{
        "comidas": [{{"lista de tipos de comida como por ejemplo ensaladas,comida rapida, comida italiana, etc"}}],
        
    }}

    texto :     {texto}
    """

)        

        self.prompt_template_ig_lugares = PromptTemplate(
    input_variables=["texto"],
    template="""
    Te voy a pasar las descripciones de fotos y los hashtags de una cuenta de Instagram de una persona, en base a las descripciones de fotos y el texto genera una lista de tipos de lugares que le gusta a esta persona, como por ejemplo: playa, ciudades, campo, desiertos, entre otros.
    La salida solo deberá ser en formato JSON, claro y limpio, con la siguiente estructura:
    {{
        "lugares": [{{"lista de tipos de lugares en terminos generales como por ejemplo playa, parques, biblioteca, hogar, etc"}}],
        "comidas": [{{"lista de tipos de comida en terminos generales como por ejemplo ensaladas,comida rapida, comida italiana, etc"}}],
         "hobbies": [{{"lista de tipos de hobbies en terminos generales como por ejemplo lectura, deportes, música, cine, etc"}}],

        
    }}

    texto :     {texto}
    """

)        
        self.chain_ig_lugares = self.prompt_template_ig_lugares | self.llm | StrOutputParser()
        self.chain_ig_comidas = self.prompt_template_ig_comidas | self.llm | StrOutputParser()
        self.chain_linkedin_estudio=self.prompt_template_linkedin_estudio | self.llm | StrOutputParser()
        self.chain_linkedin_trabajo=self.prompt_template_linkedin_trabajo | self.llm | StrOutputParser()

    def analyze_ig_lugares_comida_hobbies(self, texto):
        """
        Analyzes the Instagram data and generates a summary of places and food preferences.

        :param context: A string containing the descriptions of the photos and hashtags.
        :return: A dictionary with keys 'lugares visitados' and 'comidas'.
        """
        try:
            result = self.chain_ig_lugares.invoke(texto)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def analyze_ig_comidas(self, texto):

        try:
            result = self.chain_ig_comidas.invoke(texto)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def analyze_linkedin_trabajo(self, texto):
  
        try:
            result = self.chain_linkedin_trabajo.invoke(texto)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None    

    def analyze_linkedin_estudio(self, texto):

        try:
            result = self.chain_linkedin_estudio.invoke(texto)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None        
    
        
