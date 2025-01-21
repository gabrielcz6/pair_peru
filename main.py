
from perfilanalyzer import PerfilAnalyzer



#esta funcion recibe 4 perametros, ig_user, linkedin_user, gender "M" o "F" y "su id unico"
perfil = PerfilAnalyzer("gabrielcz6", "gabrielinteligenciaartificial","M","13")

file_path = perfil.analizar_perfil()




print(f"Perfil analizado y guardado en: {file_path}")


