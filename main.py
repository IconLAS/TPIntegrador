from fastapi import FastAPI

app = FastAPI()



@app.get("/")

def inicio(): 
    return {"mensaje":"API de la biblioteca"}

@app.get("/libros")

def listar_libros(libros_registrados=None):
   
    if not libros_registrados:
        print('no hay libros :p')
    else:
        return libros_registrados



@app.get("/libros/buscar")

def buscar_libros_en_la_lista():
    return 