import json

def parse_json_from_string(result_linkedin_trabajo):
    # Eliminar 'json\n' y los backticks '```'
    result_linkedin_trabajo = result_linkedin_trabajo.replace('json\n', '')
    result_linkedin_trabajo = result_linkedin_trabajo.replace("```", "")
    
    # Convertir todo a minúsculas y quitar tildes
    result_linkedin_trabajo = result_linkedin_trabajo.lower()

    # Reemplazar todas las vocales acentuadas y caracteres especiales
    result_linkedin_trabajo = result_linkedin_trabajo.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u') \
                                                   .replace('à', 'a').replace('è', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u') \
                                                   .replace('ä', 'a').replace('ë', 'e').replace('ï', 'i').replace('ö', 'o').replace('ü', 'u') \
                                                   .replace('â', 'a').replace('ê', 'e').replace('î', 'i').replace('ô', 'o').replace('û', 'u') \
                                                   .replace('ã', 'a').replace('õ', 'o').replace('ñ', 'n') \
                                                   .replace('ç', 'c').replace('ý', 'y').replace('ÿ', 'y') \
                                                   .replace('¡', '').replace('¿', '') \
                                                   .replace('°', '')  # Si es necesario eliminar otros caracteres
    
    try:
        # Intentar analizar el JSON
        data = json.loads(result_linkedin_trabajo)
        return data
    except json.JSONDecodeError as e:
        print(f"json decode error: {e}")
        return None
    

import json

def combinar_datos(result_linkedin_trabajo, result_linkedin_estudio, result_ig_lugares_comida_hobbie, resultado_ig_fotos):
    # Combinación de los datos
    unified_data = {
        "trabajo": result_linkedin_trabajo["tipostrabajo"],
        "estudio": {
            "carrera": result_linkedin_estudio["carrera"],
            "especialidad": result_linkedin_estudio["especialidad"]
        },
        "lugares": resultado_ig_fotos["lugares"],
        "comidas": list(set(result_ig_lugares_comida_hobbie["comidas"] + resultado_ig_fotos["comidas"])),
        "hobbies": list(set(result_ig_lugares_comida_hobbie["hobbies"] + resultado_ig_fotos["hobbies"])),
        "lugares": resultado_ig_fotos["lugares"],
    }
    
    # Mostrar el resultado
    return json.dumps(unified_data, indent=4, ensure_ascii=False)

def combinar_lugares_comidas_hobbies(dict1, dict2):
    # Combinar datos eliminando duplicados
    unified_data = {
        "lugares": list(set(dict1["lugares"] + dict2["lugares"])),
        "comidas": list(set(dict1["comidas"] + dict2["comidas"])),
        "hobbies": list(set(dict1["hobbies"] + dict2["hobbies"]))
    }
    
    # Retornar el resultado como diccionario
    return unified_data
