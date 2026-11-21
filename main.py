#Imports
from fastapi import FastAPI


# Iniciar la app

app = FastAPI()
        

    

      
# Rutas del método GET


""" @app.get("/")
def inicio(status_code=200,{"mensaje":"API de la biblioteca"}): 


@app.get("/libros")
    def listar_libros(status_code=200, libros_guardados=[]):
    return libros_guardados



@app.get("/libros/{id}")

def buscar_por_id(id):
    pass  """


# Rutas del método POST
@app.post('/libros')
def crear_libro(Libro):
    pass

# Rutas del método PUT



# Rutas del método DELETE