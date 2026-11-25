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
ARCHIVO_LIBRO= DATOS_DIR / "libros.json" #nombre de la ruta de los libros
DATOS_DIR.mkdir(exist_ok=True) # Asegura que el directorio es creado solo si no existe, en cuanto al archivo, su existencia se maneja abajo.
try:
    with open(ARCHIVO_LIBRO, "r", encoding="utf-8") as archivo_registro: # Se abre el archivo de registro
        datos = json.load(archivo_registro) # Se guarda en memoria
    libros = datos # Fuera de la funcion, se guardan los datos
except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError, KeyError, IndexError): #Si falla cualquier cosa
    libros=[] #creamos la variable como lista vacía, ESTO SIEMPRE ES ACCESIBLE SI HAY ERROR
if not isinstance(libros, list): libros= [] # En caso de que el except no haya atrapado nada, por profilaxis, se verifica que al menos sea una lista, si no, es lista vacía, igual que arriba pero ahora libros existe como variable dentro del try y afuera. SIEMPRE ES ACCESIBLE
try:
    max_id= max((l["id"] for l in libros), default=0) # Con mucha ayuda de Claude... la variable usa la funcion max que retorna el int máximo->atributo del objeto libro obtenido al recorrer la lista libros, si la lista no tiene elementos default 0
except(KeyError, TypeError): # Como asumo que la lista tiene un objeto con primer campo id, si el key no es id, o el tipo no se puede recorrer, por ejemplo, libros=[{"identificador":..}]-> KeyError; libros=[1,2]-> TypeError
    max_id=0 # Si ocurrio uno de esos errores, definimos la variable
    libros=[] #Ultra repetitivo, es mas que nada porque no pude organizarme en un mismo bloque, lo dividí en tres y sinceramente pensar más en esto es por gusto más que por necesidad

def guardar_datos(): # Se define una funcion que siembre se puede invocar para escribir en el archivo
    with open(ARCHIVO_LIBRO, "w", encoding="utf-8") as archivo_libros: # Que abre el archivo en modo escritura
        json.dump(libros, archivo_libros, indent=2, ensure_ascii=False) # Le dice al json que le encaje la variable libros a ese archivo, lo idente en 2,, para que sea legible y cuide que el ascii no para que lo que pueda llevar utf-8 lo lleve

guardar_datos() #Se ejecuta la función así nomas, y siempre se ejecuta así nomas porque usa la lista de libros en memoria.
# Clase Libro con Pydantic 

class Libro(BaseModel): # Modelo libro no lleva id, no es util agregarselo, despues sde le agrtega a mano y listo
    titulo: str = Field(min_length=3, max_length=100, pattern=r"^[^áàéèíìóòúùÁÀÉÈÍÌÓÒÚÙ]*$")
    autor: str = Field(min_length=3, max_length=60)
    anio: int= Field(ge=1000, le=2100)
    disponible: bool = True  

class LibroPatch(BaseModel): # Para el patch como se toman campos especificos Claude recomendo esto
    titulo: str| None = Field(min_length=3, max_length=100, pattern=r"^[^áàéèíìóòúùÁÀÉÈÍÌÓÒÚÙ]*$", default=None)
    autor: str | None = Field(min_length=3, max_length=60, default=None)
    anio: int | None= Field( ge=1000, le=2100, default=None)
    disponible: bool | None = Field(default=None) # Todos los campos son iguales pero opcionales, se prioriza que cumplan tipos y solo se utilizan los que cumplen, se implementa bien.
#-----------------------------Funciones repetidas---------------------------------------------
def traer_libro_por_id(id): # Abstraccion de algo super util
    for l in libros:
        if l["id"] == id:
            return l       
    raise HTTPException(status_code=404, detail="No se encuentra libro con ese id")
#---------------------- Funciones para Query Params------------------------------------------------------------
#----------------Abstracciones porque la ruta sino era muy larga-----------------------------------------------
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

def por_string(texto:str): #Acá ya aplique comprension de listas y todo este asunto
   string= texto.lower() # para olvidarme de la conversión
   resultado = [l for l in libros if string in l["titulo"].lower() or string in l["autor"].lower()] 
   '''toda la logica acá, igual en la logica de negocio hay mucho espacio 
        para una mala implementacion.'''
   return resultado
   
    
# ---------------------Rutas del método GET---------------------------------------------------

@app.get("/")
def inicio():
    return {"mensaje":"API de la biblioteca"} # :ok:


'''La ruta acepta un monton de Queryparams, se implementan la Query de fastapi
 para manejar minimos, maximos no puse porque es slicing y segun Claude es válido devolver []
se podría manejar...'''
@app.get("/libros")

def listar_libros(autor:str|None=None,disponible:bool|None=None,
                  limite:int= Query(20, ge=0,), desde:int= Query(0, ge=0)):
    if autor and disponible is not None:
        resultado= por_disponibilidad_y_autor(buscar_por_autor(autor), buscar_por_disponibilidad(disponible))
    elif autor:
        resultado= buscar_por_autor(autor)
    elif disponible is not None:
        resultado = buscar_por_disponibilidad(disponible)        
    else:
        resultado= libros
    return resultado[desde: desde + limite]

'''Me ayudo una banda Claude: Me planteó mucho el uso de comprension de listas 
para evitar tanta creacion de variables y repetir if dentro de un for etc,
también a la hora de encadenar funciones en vez de intersectar
pasandole listas como parametro en la construccion de las funciones arriba. 
No lo implemente porque ya estoy fuera de término, menos voy a cancherear...
El próximo TP sin falta.'''
    

@app.get('/libros/buscar')
def listar_coincidencias(texto:str = Query(min_length=1)):
    return por_string(texto)
    
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
    

# ---------------------Rutas con parametros de ruta----------------------------------------------------
# ---------------------Rutas del método GET---------------------------------------------------
@app.get("/libros/{id}")
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
    libro.update(datos.model_dump(exclude_unset=True, exclude_none=True)) # se omiten campos vacíos, esto en PUT no ocurre porque utiliza el modelo base 
    guardar_datos()
    return libro


            
    
        
          
                
          