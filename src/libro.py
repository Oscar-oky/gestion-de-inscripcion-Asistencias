from db_connection import get_conn

class Libro:
    def __init__(self, id_, titulo, autor, disponible=True):
        self.id = id_
        self.titulo = titulo
        self.autor = autor
        self.disponible = bool(disponible)

    def prestar(self, usuario_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            # Verificar disponibilidad actual
            cur.execute("SELECT disponible FROM libros WHERE id = %s FOR UPDATE", (self.id,))
            row = cur.fetchone()
            if not row:
                return False
            disponible = bool(row[0])
            if not disponible:
                return False

            # Actualizar libro y crear préstamo
            cur.execute("UPDATE libros SET disponible = 0 WHERE id = %s", (self.id,))
            cur.execute(
                "INSERT INTO prestamos (usuario_id, libro_id) VALUES (%s, %s)",
                (usuario_id, self.id)
            )
            conn.commit()
            self.disponible = False
            return True
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def devolver(self, usuario_id):
        conn = get_conn()
        try:
            cur = conn.cursor()
            # Buscar préstamo no devuelto para este usuario y libro
            cur.execute("""
                SELECT id FROM prestamos
                WHERE usuario_id = %s AND libro_id = %s AND devuelto = 0
                ORDER BY fecha_prestamo DESC LIMIT 1
            """, (usuario_id, self.id))
            row = cur.fetchone()
            if not row:
                return False
            prestamo_id = row[0]
            cur.execute("UPDATE prestamos SET devuelto = 1, fecha_devolucion = NOW() WHERE id = %s", (prestamo_id,))
            cur.execute("UPDATE libros SET disponible = 1 WHERE id = %s", (self.id,))
            conn.commit()
            self.disponible = True
            return True
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    # Métodos de clase para CRUD
    @classmethod
    def crear(cls, titulo, autor):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO libros (titulo, autor) VALUES (%s, %s)", (titulo, autor))
            conn.commit()
            lid = cur.lastrowid
            return cls(lid, titulo, autor, True)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, autor, disponible FROM libros ORDER BY titulo")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_titulo(cls, titulo):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, autor, disponible FROM libros WHERE titulo = %s", (titulo,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, titulo, autor, disponible FROM libros WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2], r[3]) if r else None
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        status = "Disponible" if self.disponible else "Prestado"
        return f"{self.titulo} - {self.autor} ({status})"