# sistema_eventos.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from db_connection import get_conn

# ==================== CLASES POO ====================
class Usuario:
    def __init__(self, id, nombre, email, rol="usuario"):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.rol = rol

class Organizador(Usuario):
    def __init__(self, id, nombre, email):
        super().__init__(id, nombre, email, "organizador")

# ==================== FUNCIONES BD ====================
def listar_eventos_publicados():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.titulo, e.fecha, e.hora_inicio, e.lugar, e.capacidad_maxima,
               COUNT(i.id) as inscritos
        FROM eventos e
        LEFT JOIN inscripciones i ON e.id = i.evento_id AND i.estado = 'confirmada'
        WHERE e.estado = 'publicado'
        GROUP BY e.id
        ORDER BY e.fecha
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def inscribirse(usuario_id, evento_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT capacidad_maxima FROM eventos WHERE id = %s", (evento_id,))
        capacidad = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM inscripciones WHERE evento_id = %s AND estado = 'confirmada'", (evento_id,))
        actuales = cursor.fetchone()[0]
        
        if actuales >= capacidad:
            return False, "No hay cupo disponible"
            
        cursor.execute("""
            INSERT INTO inscripciones (usuario_id, evento_id) 
            VALUES (%s, %s)
        """, (usuario_id, evento_id))
        conn.commit()
        return True, "¡Inscripción exitosa!"
    except Exception as e:
        conn.close()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

# ==================== INTERFAZ GRÁFICA ====================
root = tk.Tk()
root.title("Gestión de Eventos - ISW-25 | Oscar Alexandro Morales Galván")
root.geometry("1200x700")
root.configure(bg="#f0f4f8")

# Usuario actual (simulado)
current_user = Usuario(1, "Oscar Alexandro Morales Galván", "oscar@alumno.upsr.edu.mx")

# Header
header = tk.Frame(root, bg="#1B5E20", height=100)
header.pack(fill="x")
tk.Label(header, text="Sistema de Inscripción y Asistencia a Eventos", 
         font=("Helvetica", 20, "bold"), fg="white", bg="#1B5E20").pack(pady=25)

# Bienvenida
tk.Label(root, text=f"Bienvenido: {current_user.nombre}", font=("Arial", 12), bg="#f0f4f8").pack(pady=10)

# Tabla de eventos
columns = ("ID", "Título", "Fecha", "Hora", "Lugar", "Capacidad", "Inscritos")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="center")
tree.pack(padx=20, pady=20, fill="both", expand=True)

def actualizar_lista():
    for item in tree.get_children():
        tree.delete(item)
    eventos = listar_eventos_publicados()
    for ev in eventos:
        tree.insert("", "end", values=ev)

def inscribirse_evento():
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Seleccionar", "Por favor selecciona un evento")
        return
    evento_id = tree.item(seleccion[0])["values"][0]
    ok, msg = inscribirse(current_user.id, evento_id)
    messagebox.showinfo("Resultado", msg)
    if ok:
        actualizar_lista()

# Botones
btn_frame = tk.Frame(root, bg="#f0f4f8")
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Actualizar Lista", bg="#2196F3", fg="white", font=("Arial", 12), command=actualizar_lista).pack(side="left", padx=10)
tk.Button(btn_frame, text="Inscribirme", bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), width=20, command=inscribirse_evento).pack(side="left", padx=20)

# Pie de página
footer = tk.Frame(root, bg="#1B5E20", height=50)
footer.pack(fill="x", side="bottom")
tk.Label(footer, text="© 2025 Oscar Alexandro Morales Galván - ISW-25 | Politécnica Santa Rosa", fg="white", bg="#1B5E20").pack(pady=10)

# Cargar eventos al inicio
actualizar_lista()

root.mainloop()