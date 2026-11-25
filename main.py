#Imports
from fastapi import FastAPI, HTTPException, Query, Path 
from pydantic import BaseModel, Field 
import json
import csv
from pathlib import Path as RutaJSON
# Iniciar la app
app = FastAPI()

# Path del archivo libros.json:

DATOS_DIR = RutaJSON(__file__).parent / "datos" # Nombra la carpeta del archivo .json
ARCHIVO_LIBRO= DATOS_DIR / "libros.json"
DATOS_DIR.mkdir(exist_ok=True) # Asegura que el directorio es creado solo si no existe, en cuanto al archivo,. su existencia se maneja abajo.
try:
    with open(ARCHIVO_LIBRO, "r", encoding="utf-8") as archivo_registro:
        datos = json.load(archivo_registro) 
    libros = datos 
except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError, KeyError, IndexError):
    libros=[]
if not isinstance(libros, list): libros= [] #Si libros no se esta recibiendo correctamente en "datos", es vacía.    
try:
    max_id= max((l["id"] for l in libros), default=0) #Acá la IA me hizo comerme un viaje, no me gusta por orgullo pero se explicar el funcionamiento
except(KeyError, TypeError):
    max_id=0
    libros=[]

def guardar_datos():
    with open(ARCHIVO_LIBRO, "w", encoding="utf-8") as archivo_libros:
        json.dump(libros, archivo_libros, indent=2, ensure_ascii=False)       

guardar_datos()
# Clase Libro con Pydantic 
         

class Libro(BaseModel):
    titulo: str = Field(min_length=3, max_length=100, pattern=r"^[^áàéèíìóòúùÁÀÉÈÍÌÓÒÚÙ]*$")
    autor: str = Field(min_length=3, max_length=60)
    anio: int= Field(ge=1000, le=2100)
    disponible: bool = True  

class LibroPatch(BaseModel):
    titulo: str| None = Field(min_length=3, max_length=100, pattern=r"^[^áàéèíìóòúùÁÀÉÈÍÌÓÒÚÙ]*$", default=None)
    autor: str | None = Field(min_length=3, max_length=60, default=None)
    anio: int | None= Field( ge=1000, le=2100, default=None)
    disponible: bool | None = Field(default=None)
#-----------------------------Funciones repetidas---------------------------------------------
def traer_libro_por_id(id):
    for l in libros:
        if l["id"] == id:
            return l       
    raise HTTPException(status_code=404, detail="No se encuentra libro con ese id")
#---------------------- Funciones para Query Params------------------------------------------------------------
def buscar_por_autor(autor:str):
    libros_por_autor=[]
    for l in libros:    
        if l["autor"].lower().strip() == autor.lower().strip():
            libros_por_autor.append(l)
    return libros_por_autor

def buscar_por_disponibilidad(disponible:bool):
    libros_por_disponibilidad=[]
    for l in libros:
        if l["disponible"] == disponible:
            libros_por_disponibilidad.append(l)
    return libros_por_disponibilidad

def por_disponibilidad_y_autor(autor:list, disponibles:list):
    resultado=[]
    for l in autor:
        if l in disponibles:
            resultado.append(l)
    return resultado
            
    
# ---------------------Rutas con Variables----------------------------------------------------

@app.get("/")
def inicio():
    return {"mensaje":"API de la biblioteca"} # :ok:


@app.get("/libros")
def listar_libros(autor:str|None=None,disponible:bool|None=None,
                  limite:int= Query(10, ge=0,), desde:int= Query(0, ge=0)):
    if autor and disponible is not None:
        resultado= por_disponibilidad_y_autor(buscar_por_autor(autor), buscar_por_disponibilidad(disponible))
    elif autor:
        resultado= buscar_por_autor(autor)
    elif disponible is not None:
        
        resultado = buscar_por_disponibilidad(disponible)        
    else:
        resultado= libros
    return resultado[desde: desde + limite]

    
'''Me ayudo una banda Claude Me planteo mucho el uso de comprension de listas para evitar los if dentro de los recorridos for
también a la hora deencadenar funciones en vez de intersectar, pasandole listas como parametro. Una maravilla '''
    

@app.get('/libros/buscar', status_code=200)
def libros_que_contengan(texto:str=''):
    return

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
    

#---------------------------------------------------------------------------------------------
# ---------------------Rutas del método GET---------------------------------------------------
@app.get("/libros/{id}", status_code=200)
def buscar_libro_por_id(id:int= Path(ge=1)):
     return traer_libro_por_id(id)
     
        

# --------------------------------Ruta DELETE------------------------------------------------
@app.delete("/libros/{id}", status_code=204)
def eliminar_libro(id: int= Path(ge=1)):
    libro= traer_libro_por_id(id)
    libros.remove(libro)
    guardar_datos()
    return 
    
# --------------------------------Ruta PUT---------------------------------------------------
@app.put("/libros/{id}", status_code=200)
def modificar_libro(datos:Libro, id:int=Path(ge=1)):
    if datos: 
        libro=traer_libro_por_id(id)
        libro.update(datos.model_dump())
        guardar_datos()
        return libro

# --------------------------------Ruta PATCH---------------------------------------------------
@app.patch("/libros/{id}")
def parchear_dato(datos:LibroPatch, id:int= Path(ge=1)):
    libro= traer_libro_por_id(id)
    libro.update(datos.model_dump(exclude_unset=True, exclude_none=True)) # se omiten campos vacíos, esto en PUT no ocurre porque utiliza el modelo base, con 
    guardar_datos()
    return libro


            
    
        
          
                
          