import json

class Libro:
    def __innit__(self):
        self.titulo = None
        self.autor = None
        self.anio = None
        self.disponible = True
    def __str__(self):
        print(self.titulo)
    def cargar_libro(self):
        self.titulo= str(input('Ingresa el nombre del libro :_'))
        self.autor= str(input('Ingresa el autor del libro :_'))
        self.anio= int(input('Ingresa el nombre del libro :_'))
    def retirar_libro(self):
        if self.disponible:
            self.disponible = not self.disponible
    def devolver_libro(self):
        if self.disponible == False:
            self.disponible = not self.disponible
    
# Dentro de lo que respecta al la inversion de un valor booleano resulta que "Con el operador XOR (^=): Si escribes activo ^= True, también invierte el valor booleano. Sin embargo, en Python se prefiere siempre activo = not activo porque es más legible y explícito."
# le saque la respuesta a Gemini :3
class ArchivoLibros:
    def __innit__(self):
        with open("libros.json", "a", encoding="utf-8") as f:
            try:
                libros_cargados= json.load(f) 
            except FileNotFoundError:
                print("Algo salió mal, muy mal...")


    

    

