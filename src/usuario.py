# usuario.py
from db_connection import get_conn
from libro import Libro
import hashlib

def hash_password(password: str) -> str:
    if password is None:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class Usuario:
    def __init__(self, id_, nombre, role='bibliotecario'):
        self.id = id_
        self.nombre = nombre
        self.role = role

    @classmethod
    def crear(cls, nombre, role='bibliotecario', password=None):
        conn = get_conn()
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password) if password else None
            cur.execute(
                "INSERT INTO usuarios (nombre, role, password) VALUES (%s, %s, %s)",
                (nombre, role, pwd_hash)
            )
            conn.commit()
            uid = cur.lastrowid
            return cls(uid, nombre, role)
        finally:
            cur.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role FROM usuarios ORDER BY nombre")
            rows = cur.fetchall()
            return [cls(r[0], r[1], r[2]) for r in rows]
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_nombre(cls, nombre):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role FROM usuarios WHERE nombre = %s", (nombre,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role FROM usuarios WHERE id = %s", (id_,))
            r = cur.fetchone()
            return cls(r[0], r[1], r[2]) if r else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def autenticar(cls, nombre, password):
        """Devuelve instancia Usuario si credenciales correctas, sino None."""
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role, password FROM usuarios WHERE nombre = %s", (nombre,))
            r = cur.fetchone()
            if not r:
                return None
            stored_hash = r[3]
            if stored_hash is None:
                return None
            if hash_password(password) == stored_hash:
                return cls(r[0], r[1], r[2])
            return None
        finally:
            cur.close()
            conn.close()

    def obtener_libros_prestados(self):
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT l.id, l.titulo, l.autor, l.disponible
                FROM libros l
                JOIN prestamos p ON p.libro_id = l.id
                WHERE p.usuario_id = %s AND p.devuelto = 0
            """, (self.id,))
            rows = cur.fetchall()
            return [Libro(r[0], r[1], r[2], r[3]) for r in rows]
        finally:
            cur.close()
            conn.close()

    def __str__(self):
        return f"{self.nombre} ({self.role})"