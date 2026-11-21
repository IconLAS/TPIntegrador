from pydantic import BaseModel, Field, Optional
import json
# Path del archivo:

DATA = './data/libros.json'
# Uso del archivo libros para guardar los datos:
with open(DATA, 'r', encoding='utf-8') as f:
    
    try:

        libros = json.load(f)
    except FileNotFoundError: 
    
        with open(DATA, 'w', encoding='utf-8') as f:
            json.dump([], f)
        pass
        

class Libro(BaseModel):
    id:int 
    titulo:str = Field(min_length=3, max_length=100, strict=True, pattern=r"^[^áéíóúÁÉÍÓÚ]*$") # Acá me quede con lo que pideel pdf para no quedar loco con la inyección de código, desconozco si es posible, prefiero no saber.
    autor:str = Field(min_length=3, max_length=60, strict=True)
    anio:int = Field(ge=1000, le=2100, strict=True)
    disponible: Optional[bool] = True








    

    

