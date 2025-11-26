# biblioteca.py
from libro import Libro
from usuario import Usuario

class Biblioteca:
    def __init__(self):
        pass

    # Registro
    def registrar_libro(self, titulo, autor):
        return Libro.crear(titulo, autor)

    def registrar_usuario(self, nombre):
        return Usuario.crear(nombre)

    # Búsqueda
    def buscar_libro(self, titulo):
        return Libro.buscar_por_titulo(titulo)

    def buscar_usuario(self, nombre):
        return Usuario.buscar_por_nombre(nombre)

    # Listados (para GUI)
    def listar_libros(self):
        return Libro.listar_todos()

    def listar_usuarios(self):
        return Usuario.listar_todos()

    # Prestamo
    def prestar_libro(self, titulo, nombre_usuario):
        usuario = self.buscar_usuario(nombre_usuario)
        if usuario is None:
            return "Usuario no encontrado."
        libro = self.buscar_libro(titulo)
        if libro is None:
            return "Libro no encontrado."
        try:
            ok = libro.prestar(usuario.id)
            if ok:
                return f"{usuario.nombre} ha tomado prestado '{libro.titulo}'."
            else:
                return f"El libro '{libro.titulo}' no está disponible."
        except Exception as e:
            return f"Error al prestar: {e}"

    # Devolución
    def devolver_libro(self, titulo, nombre_usuario):
        usuario = self.buscar_usuario(nombre_usuario)
        if usuario is None:
            return "Usuario no encontrado."
        libro = self.buscar_libro(titulo)
        if libro is None:
            return "Libro no encontrado."
        try:
            ok = libro.devolver(usuario.id)
            if ok:
                return f"'{libro.titulo}' ha sido devuelto por {usuario.nombre}."
            else:
                return "No existe préstamo activo para este usuario y libro."
        except Exception as e:
            return f"Error al devolver: {e}"