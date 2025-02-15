"""
Imagina que esta API es un informe de muestras sobre la calidad del agua tomadas de diferentes lugares de Colombia:
La función load_water() es como un almacenador que carga las mediciones del agua cuando se ejecuta.
La función get_water() muestra todas las mediciones cuando alguien lo pide.
La función get_water(id) es como si alguien preguntara por una medicion específica por su código de identificación.
La función chatbot(query) es un asistente que busca las mediciones según sus valores.
La función get_water_by_category(category) ayuda a encontrar las mediciones según su calificación.
"""

# Importamos las herramientas necesarias para contruir nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse para páginas web, JSONResponse para respuestas en formato JSON. 
import pandas as pd # Pandas nos ayuda a manejar datos en tablasm como si fuera un Excel.
import nltk # NLTK es una librería para procesar texto y analizar palabras. 
from nltk.tokenize import word_tokenize # Se usa para dividir un texto en palabras individuales.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinonimos de palabras. 
import numpy as np

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador. 
nltk.data.path.append(r'C:\Users\1\AppData\Local\Programs\Python\Python311\Lib\site-packages\nltk')

# Descargamos las herramientas necesarias de NLTK para el análisis de palabras.

nltk.download('punkt') # Paquete para dividir frases en palabras.
nltk.download('wordnet') # Paquete para encontrar sinonimos de palabras en inglés.
nltk.download('punkt_tab')

# Función para cargar las películas desde un archivo CSV

def load_water():
    # Leemos el archivo que contiene información de películas y seleccionamos las columnas más importantes
    df = pd.read_csv("Dataset/waterQuality1.csv", sep=';', converters={'id':str})

    df['is_safe'] = np.where(df['is_safe']==1,'Potable',"No potable")
    
    # Llenamos los espacios vacíos con texto vacío y convertimos los datos en una lista de diccionarios 
    return df.fillna('').to_dict(orient='records')

# Cargamos las películas al iniciar la API para no leer el archivo cada vez que alguien pregunte por ellas.
water_list = load_water()

# Función para encontrar sinónimos de una palabra

def get_synonyms(word): 
    # Usamos WordNet para obtener distintas palabras que significan lo mismo.
    return{lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicación FastAPI, que será el motor de nuestra API
# Esto inicializa la API con un nombre y una versión
app = FastAPI(title="Informe de mediciones de calidad del agua", version="1.0.0")


# Ruta de inicio: Cuando alguien entra a la API sin especificar nada, verá un mensaje de bienvenida.

@app.get('/', tags=['Home'])
def home():
# Cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida
    return HTMLResponse('<h1>Bienvenido al informe de mediciones de calidad del agua</h1>')

# Obteniendo la lista de películas
# Creamos una ruta para obtener todas las películas

# Ruta para obtener todas las películas disponibles

@app.get('/water', tags=['Water'])
def get_water():
    # Si hay películas, las enviamos, si no, mostramos un error
    return water_list or HTTPException(status_code=500, detail="No hay datos de mediciones de calidad de agua disponibles, valide con el laboratorio")


# Ruta para obtener una medición específica según su ID
@app.get('/water/{id}', tags=['Water'])
def get_water(id: str):
    # Buscamos en la lista de mediciones la que tenga el mismo ID
    return next((m for m in water_list if m['id'] == id), {"detalle": "medición no encontrada"})


# Ruta del chatbot que responde con películas según palabras clave de la categoría

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave, para entender mejor la intención del usuario
    query_words = word_tokenize(query.lower())
    
    # Buscamos sinónimos de las palabras clave para ampliar la búsqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)

    # Filtramos la lista de películas buscando coincidencias en la categoría
    results = [m for m in water_list if any (s in m['is_safe'].lower() for s in synonyms)]

     # Si encontramos mediciones, enviamos la lista; si no, mostramos un mensaje de que no se encontraron coincidencias
    
    return JSONResponse (content={
        "respuesta": "Aquí tienes algunas mediciones relacionadas." if results else "No encontré mediciones con esa calificación.",
        "mediciones": results
    })


# Ruta para buscar mediciones por calificación específica

@app.get ('/water/by_is_safe/', tags=['Water'])
def get_water_by_is_safe(is_safe: str):
    # Filtramos la lista de mediciones según la calificación ingresada
    return [m for m in water_list if is_safe.lower() in m['is_safe'].lower()]
