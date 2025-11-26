# src/execute_events.py
# VERSIÓN FINAL CORREGIDA - Registro y Login 100% FUNCIONAL
# Oscar Alexandro Morales Galván - ISW-25

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
from db_connection import get_conn

# ======================= UTILIDADES =======================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ======================= CLASES POO =======================
class Persona:
    def __init__(self, id, nombre, apellidos, email):
        self.id = id
        self.nombre = nombre
        self.apellidos = apellidos
        self.email = email

class Usuario(Persona):
    def __init__(self, id, nombre, apellidos, email):
        super().__init__(id, nombre, apellidos, email)
        self.rol = "usuario"

class Organizador(Persona):
    def __init__(self, id, nombre, apellidos, email, departamento=""):
        super().__init__(id, nombre, apellidos, email)
        self.rol = "organizador"
        self.departamento = departamento

# ======================= VARIABLES GLOBALES =======================
current_user = None
root = None
tree_global = None

# ======================= REGISTRO =======================
def registrar_usuario():
    global current_user
    win = tk.Toplevel(root)
    win.title("Registro Nuevo Usuario")
    win.geometry("450x600")
    win.configure(bg="#f0f0f0")
    win.grab_set()  # Bloquea la ventana principal

    tk.Label(win, text="CREAR CUENTA NUEVA", font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="#1B5E20").pack(pady=20)

    datos = {}
    campos = ["Nombre", "Apellidos", "Correo electrónico", "Contraseña", "Repetir contraseña", "Teléfono (opcional)"]
    for campo in campos:
        tk.Label(win, text=campo + ":", bg="#f0f0f0", font=("Arial", 10)).pack(anchor="w", padx=50)
        entry = tk.Entry(win, width=40, font=("Arial", 10))
        if "contraseña" in campo.lower():
            entry.config(show="*")
        entry.pack(pady=4, padx=50)
        datos[campo] = entry

    rol_var = tk.StringVar(value="usuario")
    tk.Label(win, text="Tipo de cuenta:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(anchor="w", padx=50, pady=(20,5))
    tk.Radiobutton(win, text="Usuario (Público general)", variable=rol_var, value="usuario", bg="#f0f0f0").pack(anchor="w", padx=70)
    tk.Radiobutton(win, text="Organizador (Personal institución)", variable=rol_var, value="organizador", bg="#f0f0f0").pack(anchor="w", padx=70)

    def guardar():
        global current_user
        nombre = datos["Nombre"].get().strip()
        apellidos = datos["Apellidos"].get().strip()
        email = datos["Correo electrónico"].get().strip().lower()
        pwd1 = datos["Contraseña"].get()
        pwd2 = datos["Repetir contraseña"].get()
        telefono = datos["Teléfono (opcional)"].get().strip()
        rol = rol_var.get()

        if not all([nombre, apellidos, email, pwd1]):
            messagebox.showerror("Error", "Todos los campos obligatorios son requeridos")
            return
        if pwd1 != pwd2:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        if "@" not in email:
            messagebox.showerror("Error", "Correo inválido")
            return

        conn = get_conn()
        cur = conn.cursor()
        try:
            hash_pwd = hash_password(pwd1)
            if rol == "organizador":
                dept = simpledialog.askstring("Organizador", "Departamento:", parent=win)
                cur.execute("""INSERT INTO organizadores (nombre, apellidos, email, password_hash, departamento) 
                               VALUES (%s, %s, %s, %s, %s)""", 
                               (nombre, apellidos, email, hash_pwd, dept or "Sin especificar"))
                user_id = cur.lastrowid
                current_user = Organizador(user_id, nombre, apellidos, email, dept)
            else:
                cur.execute("""INSERT INTO usuarios (nombre, apellidos, email, password_hash, telefono) 
                               VALUES (%s, %s, %s, %s, %s)""", 
                               (nombre, apellidos, email, hash_pwd, telefono or None))
                user_id = cur.lastrowid
                current_user = Usuario(user_id, nombre, apellidos, email)

            conn.commit()
            messagebox.showinfo("ÉXITO", f"¡Cuenta creada correctamente!\nBienvenido {nombre} {apellidos}")
            win.destroy()
            win.update()
            # AQUÍ ESTABA EL ERROR: ¡Faltaba llamar a la interfaz principal!
            iniciar_sesion_exitoso()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la cuenta:\n{e}")
        finally:
            cur.close()
            conn.close()

    tk.Button(win, text="CREAR CUENTA", bg="#4CAF50", fg="white", font=("bold", 14), width=25, command=guardar).pack(pady=30)

# ======================= LOGIN =======================
def login():
    global current_user
    if messagebox.askyesno("Sistema de Eventos", "¿Ya tienes una cuenta?"):
        email = simpledialog.askstring("Iniciar Sesión", "Correo electrónico:", parent=root)
        if not email: return
        pwd = simpledialog.askstring("Iniciar Sesión", "Contraseña:", show="*", parent=root)
        if not pwd: return

        conn = get_conn()
        cur = conn.cursor()
        hash_pwd = hash_password(pwd)

        # Buscar organizador
        cur.execute("SELECT id, nombre, apellidos, email, departamento FROM organizadores WHERE email=%s AND password_hash=%s", (email.lower(), hash_pwd))
        row = cur.fetchone()
        if row:
            current_user = Organizador(row[0], row[1], row[2], row[3], row[4])
        else:
            # Buscar usuario normal
            cur.execute("SELECT id, nombre, apellidos, email FROM usuarios WHERE email=%s AND password_hash=%s", (email.lower(), hash_pwd))
            row = cur.fetchone()
            if row:
                current_user = Usuario(row[0], row[1], row[2], row[3])

        cur.close()
        conn.close()

        if current_user:
            messagebox.showinfo("Éxito", f"Bienvenido {current_user.nombre} {current_user.apellidos}")
            iniciar_sesion_exitoso()
        else:
            messagebox.showerror("Error", "Correo o contraseña incorrectos")
    else:
        registrar_usuario()

# ======================= INTERFAZ PRINCIPAL =======================
def iniciar_sesion_exitoso():
    global tree_global
    for widget in root.winfo_children():
        widget.destroy()

    root.title(f"Eventos UPSR - {current_user.nombre} {current_user.apellidos} ({current_user.rol.upper()})")

    # Header
    header = tk.Frame(root, bg="#1B5E20", height=100)
    header.pack(fill="x")
    tk.Label(header, text="Gestión de Inscripción y Asistencia a Eventos", font=("Helvetica", 18, "bold"), fg="white", bg="#1B5E20").pack(pady=20)
    tk.Label(header, text="Oscar Alexandro Morales Galván - ISW-25 - 10/10/2025", fg="#c8e6c9", bg="#1B5E20").pack()

    # Menú
    menubar = tk.Menu(root)
    menu = tk.Menu(menubar, tearoff=0)
    menu.add_command(label="Actualizar eventos", command=cargar_eventos)
    menu.add_command(label="Inscribirme", command=inscribirse)
    if current_user.rol == "organizador":
        menu.add_separator()
        menu.add_command(label="Crear evento", command=lambda: messagebox.showinfo("Próximamente", "En desarrollo"))
    menu.add_separator()
    menu.add_command(label="Cerrar sesión", command=cerrar_sesion)
    menubar.add_cascade(label="Menú", menu=menu)
    root.config(menu=menubar)

    # Tabla
    frame = tk.Frame(root, bg="white")
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    tree_global = ttk.Treeview(frame, columns=("ID","Título","Fecha","Hora","Lugar","Cupo","Inscritos"), show="headings", height=20)
    for col in tree_global["columns"]:
        tree_global.heading(col, text=col)
        tree_global.column(col, width=160, anchor="center")
    tree_global.pack(fill="both", expand=True)

    # Botones
    btns = tk.Frame(root)
    btns.pack(pady=10)
    tk.Button(btns, text="Actualizar Lista", bg="#1976d2", fg="white", command=cargar_eventos).pack(side="left", padx=10)
    tk.Button(btns, text="Inscribirme", bg="#4caf50", fg="white", font=("bold", 12), command=inscribirse).pack(side="left", padx=20)

    cargar_eventos()

def cargar_eventos():
    if tree_global is None: return
    for i in tree_global.get_children():
        tree_global.delete(i)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, e.titulo, e.fecha, e.hora_inicio, e.lugar, e.capacidad_maxima,
               COALESCE(COUNT(i.id),0)
        FROM eventos e
        LEFT JOIN inscripciones i ON e.id = i.evento_id AND i.estado='confirmada'
        WHERE e.estado='publicado'
        GROUP BY e.id
        ORDER BY e.fecha
    """)
    for row in cur.fetchall():
        tree_global.insert("", "end", values=row)
    cur.close()
    conn.close()

def inscribirse():
    if current_user.rol != "usuario":
        messagebox.showwarning("Permiso", "Solo usuarios pueden inscribirse")
        return
    sel = tree_global.selection()
    if not sel:
        messagebox.showwarning("Seleccionar", "Selecciona un evento")
        return
    evento_id = tree_global.item(sel[0])["values"][0]
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO inscripciones (usuario_id, evento_id) VALUES (%s, %s)", (current_user.id, evento_id))
        conn.commit()
        messagebox.showinfo("¡Listo!", "Te inscribiste correctamente")
        cargar_eventos()
    except Exception as e:
        messagebox.showerror("Error", "Ya estás inscrito o no hay cupo")
    finally:
        cur.close()
        conn.close()

def cerrar_sesion():
    global current_user, tree_global
    current_user = None
    tree_global = None
    login()

# ======================= INICIO =======================
root = tk.Tk()
root.title("Gestión de Eventos - UPSR")
root.geometry("1200x700")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Sistema de Gestión de Eventos\nPolitécnica de Santa Rosa", font=("Helvetica", 22, "bold"), bg="#f0f0f0", fg="#1B5E20").pack(pady=100)
tk.Label(root, text="Oscar Alexandro Morales Galván - ISW-25", font=("Arial", 14), bg="#f0f0f0").pack(pady=10)
tk.Button(root, text="INICIAR SISTEMA", bg="#1B5E20", fg="white", font=("bold", 18), width=25, height=2, command=login).pack(pady=50)

root.mainloop()