#Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field 
import json
import csv
from pathlib import Path
# Iniciar la app
app = FastAPI()

# Path del archivo libros.json:
DATA_DIR = Path('data') # Nombra la carpeta del archivo .json

DATA_DIR.mkdir(exist_ok=True) # Asegura que el directorio es creado solo si no existe, en cuanto al archivo,. su existencia se maneja abajo.
try:
        with open("./data/libros.json", "r", encoding="utf-8") as f: #Verifica la existencia
            libros = json.load(f) #carga la variable, por defecto es una lista vacía
except (FileNotFoundError, json.JSONDecodeError): # Si no está donde se espera/no existe, o está vacío.
    datos = [[{"max_id":0 }], ["libros"]] #se inicia en memoria, se vuelve a cargar con cada peticion de arriba.
    with open('./data/libros.json', 'w', encoding='utf-8') as f: # Se crea el archivo
            json.dump(datos, f) #Se carga con una lista vacía. Esto se actualiza cada vez que se pierde ./data
datos= ["max_id", libros]

# Clase Libro con Pydantic 
         

class Libro(BaseModel):
    titulo: str = Field(min_length=3, max_length=100,pattern=r"^[^áéíóúÁÉÍÓÚ]*$")
    autor: str = Field(min_length=3, max_length=60)
    anio: int= Field(strict=False, ge=1000, le=2100)
    disponible: bool = True  

# Rutas del método GET

@app.get("/")
def inicio():
    return {"mensaje":"API de la biblioteca"} # :ok:


@app.get("/libros")
def listar_libros(): 
    return libros 

#-----------------------------Funciones_repetidas---------------------------------------------
def traer_libro_por_id(id):
    for l in libros:
        if l["id"] == id:
            return l       
    raise HTTPException(status_code=404, detail="No se encuentra libro con ese id")

def guardar_datos(libros:list):
     with open('./data/libros.json', 'w', encoding='utf-8') as f: # Se crea el archivo
        json.dump(libros, f)
# ---------------------Rutas del método POST--------------------------------------------------
@app.post("/libros")
def crear_libro(libro: Libro):
    
    for l in libros: #Se recorren los libros y a cada uno se le asigna un
        autor_nuevo_normalizado, autor_guardado_normalizado= libro.autor.lower().strip(),l["autor"].lower().strip() 
        titulo_nuevo_normalizado, titulo_guardado_normalizado= libro.titulo.lower().strip(), l["titulo"].lower().strip()  

        # se verifica que no haya coincidencia en autor/titulo
        if titulo_guardado_normalizado != titulo_nuevo_normalizado and autor_guardado_normalizado != autor_nuevo_normalizado:
         raise HTTPException(status_code=409, detail="Ese libro ya se encuentra registrado") 
    # Id no se pasa por parametro
    # se definio previamente la variable que lo maneja linea 28
    
    nuevo_libro = {"id": id_count, **libro.model_dump()}
    libros.append(nuevo_libro)
    guardar_datos(libros)

    return HTTPException(201, nuevo_libro)
    

# ---------------------Rutas con Variables----------------------------------------------------
#---------------------------------------------------------------------------------------------
# ---------------------Rutas del método GET---------------------------------------------------
@app.get("/libros/{id}", status_code=200)
def buscar_libro_por_id(id:int):
     return traer_libro_por_id(id)
     
        

# --------------------------------Ruta DELETE------------------------------------------------
@app.delete("/libros/{id}")
def eliminar_libro(id:int):
    global id_count
    libro_a_borrar=traer_libro_por_id(id) 
    libros.remove(libro_a_borrar)
    id_count +1
    guardar_datos(libros)
    








# --------------------------------Ruta PUT---------------------------------------------------
@app.put("/libros/{id}")

def sobreescribir_libro(id:int, datos:Libro):
        for l in libros:
                buscar_por_id(id)
                l= datos.model_dump()
                raise HTTPException(404, "Ese libro no se encuentra")
        
          
                
          