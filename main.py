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
    with open("./data/libros.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    [{"max_id": max_id}], libros = datos
except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError, KeyError):
    max_id = 0
    libros = []


def guardar_datos():
    datos = [[{"max_id": max_id}], libros]
    with open("./data/libros.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
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
@app.post("/libros", status_code=201)
def crear_libro(libro: Libro):
    global max_id
    for l in libros:
        if (l["titulo"].lower().strip() == libro.titulo.lower().strip()
                and l["autor"].lower().strip() == libro.autor.lower().strip()):
            raise HTTPException(status_code=409, detail="Ese libro ya se encuentra registrado")
    max_id += 1
    nuevo_libro = {"id": max_id, **libro.model_dump()}
    libros.append(nuevo_libro)
    guardar_datos()
    return nuevo_libro
    

# ---------------------Rutas con Variables----------------------------------------------------
#---------------------------------------------------------------------------------------------
# ---------------------Rutas del método GET---------------------------------------------------
@app.get("/libros/{id}", status_code=200)
def buscar_libro_por_id(id:int):
     return traer_libro_por_id(id)
     
        

# --------------------------------Ruta DELETE------------------------------------------------
@app.delete("/libros/{id}")
def eliminar_libro(id: int):
    libro = buscar_libro_por_id(id)
    libros.remove(libro)
    guardar_datos()
    return {"mensaje": "Libro eliminado"}
    








# --------------------------------Ruta PUT---------------------------------------------------
@app.put("/libros/{id}")

def sobreescribir_libro(id:int, datos:Libro):
        for l in libros:
                buscar_por_id(id)
                l= datos.model_dump()
                raise HTTPException(404, "Ese libro no se encuentra")
        
          
                
          