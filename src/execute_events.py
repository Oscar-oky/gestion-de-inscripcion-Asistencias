# src/execute_events.py
# VERSIÓN FINAL CON ELIMINAR EVENTOS - ENTREGA 10/10/2025
# Oscar Alexandro Morales Galván - ISW-25

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
from db_connection import get_conn

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

# ======================= ELIMINAR EVENTO (NUEVO) =======================
def eliminar_evento():
    if current_user.rol != "organizador":
        messagebox.showwarning("Acceso denegado", "Solo los organizadores pueden eliminar eventos")
        return

    sel = tree_global.selection()
    if not sel:
        messagebox.showwarning("Seleccionar", "Selecciona un evento para eliminar")
        return

    evento_data = tree_global.item(sel[0])["values"]
    evento_id = evento_data[0]
    titulo = evento_data[1]

    if messagebox.askyesno("Confirmar eliminación", 
        f"¿Estás seguro de eliminar el evento?\n\n{titulo}\n\nEsta acción NO se puede deshacer."):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM inscripciones WHERE evento_id = %s", (evento_id,))
            cur.execute("DELETE FROM eventos WHERE id = %s", (evento_id,))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Éxito", f"Evento eliminado correctamente:\n{titulo}")
            cargar_eventos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

# ======================= CREAR EVENTO =======================
def crear_evento():
    if current_user.rol != "organizador":
        messagebox.showwarning("Acceso", "Solo organizadores pueden crear eventos")
        return

    win = tk.Toplevel(root)
    win.title("Crear Nuevo Evento")
    win.geometry("520x750")
    win.configure(bg="#f0f8ff")
    win.grab_set()

    tk.Label(win, text="CREAR NUEVO EVENTO", font=("Helvetica", 18, "bold"), fg="#1B5E20", bg="#f0f8ff").pack(pady=20)

    datos = {}
    campos = ["Título", "Descripción", "Fecha (YYYY-MM-DD)", "Hora inicio (HH:MM)", "Hora fin (HH:MM)", 
              "Lugar", "Capacidad máxima", "Costo (0 si gratuito)", "Categoría (Cultural, Formativo, Deportivo, Social)"]

    for campo in campos:
        tk.Label(win, text=campo + ":", bg="#f0f8ff").pack(anchor="w", padx=60)
        if campo == "Descripción":
            entry = tk.Text(win, width=50, height=6)
        else:
            entry = tk.Entry(win, width=50)
        entry.pack(pady=5, padx=60)
        datos[campo] = entry

    def guardar():
        try:
            titulo = datos["Título"].get().strip()
            desc = datos["Descripción"].get("1.0", tk.END).strip()
            fecha = datos["Fecha (YYYY-MM-DD)"].get().strip()
            hini = datos["Hora inicio (HH:MM)"].get().strip()
            hfin = datos["Hora fin (HH:MM)"].get().strip()
            lugar = datos["Lugar"].get().strip()
            cap = int(datos["Capacidad máxima"].get())
            costo = float(datos["Costo (0 si gratuito)"].get() or 0)
            cat = datos["Categoría (Cultural, Formativo, Deportivo, Social)"].get().strip()

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO eventos (titulo, descripcion, fecha, hora_inicio, hora_fin, lugar, capacidad_maxima, costo, categoria_id, organizador_id, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, (SELECT id FROM categorias_eventos WHERE nombre LIKE %s LIMIT 1), %s, 'publicado')
            """, (titulo, desc, fecha, hini, hfin, lugar, cap, costo, f"%{cat}%", current_user.id))
            conn.commit()
            messagebox.showinfo("ÉXITO", "Evento creado correctamente")
            win.destroy()
            cargar_eventos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    tk.Button(win, text="GUARDAR EVENTO", bg="#4CAF50", fg="white", font=("bold", 14), command=guardar).pack(pady=25)

# ======================= REGISTRO Y LOGIN (completo) =======================
def registrar_usuario():
    global current_user
    win = tk.Toplevel(root)
    win.title("Registro de Usuario")
    win.geometry("500x700")
    win.configure(bg="#f0f8ff")
    win.grab_set()

    tk.Label(win, text="CREAR CUENTA NUEVA", font=("Helvetica", 18, "bold"), bg="#f0f8ff", fg="#1B5E20").pack(pady=20)

    datos = {}
    campos = ["Nombre(s)", "Apellidos", "Correo electrónico", "Contraseña", "Repetir contraseña", "Teléfono (opcional)"]
    for campo in campos:
        tk.Label(win, text=campo + ":", bg="#f0f8ff", font=("Arial", 11)).pack(anchor="w", padx=70)
        entry = tk.Entry(win, width=40, font=("Arial", 11))
        if "contraseña" in campo.lower():
            entry.config(show="*")
        entry.pack(pady=6, padx=70)
        datos[campo] = entry

    tk.Label(win, text="Tipo de cuenta:", bg="#f0f8ff", font=("Arial", 11, "bold")).pack(anchor="w", padx=70, pady=(20,5))
    rol_var = tk.StringVar(value="usuario")
    tk.Radiobutton(win, text="Usuario (Alumno/Público)", variable=rol_var, value="usuario", bg="#f0f8ff").pack(anchor="w", padx=90)
    tk.Radiobutton(win, text="Organizador (Personal)", variable=rol_var, value="organizador", bg="#f0f8ff").pack(anchor="w", padx=90)

    def guardar():
        global current_user
        nombre = datos["Nombre(s)"].get().strip()
        apellidos = datos["Apellidos"].get().strip()
        email = datos["Correo electrónico"].get().strip().lower()
        pwd1 = datos["Contraseña"].get()
        pwd2 = datos["Repetir contraseña"].get()
        telefono = datos["Teléfono (opcional)"].get().strip()
        rol = rol_var.get()

        if not all([nombre, apellidos, email, pwd1]) or pwd1 != pwd2:
            messagebox.showerror("Error", "Verifica los datos")
            return

        conn = get_conn()
        cur = conn.cursor()
        try:
            hash_pwd = hash_password(pwd1)
            if rol == "organizador":
                dept = simpledialog.askstring("Departamento", "Departamento:", parent=win)
                cur.execute("INSERT INTO organizadores (nombre, apellidos, email, password_hash, departamento) VALUES (%s, %s, %s, %s, %s)",
                            (nombre, apellidos, email, hash_pwd, dept or "Sin departamento"))
                current_user = Organizador(cur.lastrowid, nombre, apellidos, email, dept)
            else:
                cur.execute("INSERT INTO usuarios (nombre, apellidos, email, password_hash, telefono) VALUES (%s, %s, %s, %s, %s)",
                            (nombre, apellidos, email, hash_pwd, telefono or None))
                current_user = Usuario(cur.lastrowid, nombre, apellidos, email)
            conn.commit()
            messagebox.showinfo("ÉXITO", "Cuenta creada")
            win.destroy()
            iniciar_sesion_exitoso()
        except Exception as e:
            messagebox.showerror("Error", f"Usuario ya existe: {e}")
        finally:
            cur.close()
            conn.close()

    tk.Button(win, text="CREAR CUENTA", bg="#4CAF50", fg="white", font=("bold", 14), width=30, command=guardar).pack(pady=30)

def login():
    global current_user
    if messagebox.askyesno("Sistema de Eventos", "¿Ya tienes una cuenta?"):
        email = simpledialog.askstring("Login", "Correo:", parent=root)
        pwd = simpledialog.askstring("Login", "Contraseña:", show="*", parent=root)
        if not email or not pwd: return

        conn = get_conn()
        cur = conn.cursor()
        hash_pwd = hash_password(pwd)
        cur.execute("SELECT id, nombre, apellidos, email, departamento FROM organizadores WHERE email=%s AND password_hash=%s", (email.lower(), hash_pwd))
        row = cur.fetchone()
        if row:
            current_user = Organizador(*row)
        else:
            cur.execute("SELECT id, nombre, apellidos, email FROM usuarios WHERE email=%s AND password_hash=%s", (email.lower(), hash_pwd))
            row = cur.fetchone()
            if row:
                current_user = Usuario(*row)
        cur.close()
        conn.close()

        if current_user:
            iniciar_sesion_exitoso()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
    else:
        registrar_usuario()

# ======================= INTERFAZ PRINCIPAL CON BOTÓN ELIMINAR =======================
def iniciar_sesion_exitoso():
    global tree_global
    for w in root.winfo_children():
        w.destroy()

    root.title(f"Eventos UPSR - {current_user.nombre} {current_user.apellidos}")

    # Header
    header = tk.Frame(root, bg="#1B5E20", height=110)
    header.pack(fill="x")
    tk.Label(header, text="Gestión de Inscripción y Asistencia a Eventos", font=("Helvetica", 18, "bold"), fg="white", bg="#1B5E20").pack(pady=20)
    tk.Label(header, text="Oscar Alexandro Morales Galván | ISW-25 | 10/10/2025", fg="#c8e6c9", bg="#1B5E20").pack()

    # Menú
    menubar = tk.Menu(root)
    menu = tk.Menu(menubar, tearoff=0)
    menu.add_command(label="Actualizar", command=cargar_eventos)
    menu.add_command(label="Inscribirme", command=inscribirse)
    if current_user.rol == "organizador":
        menu.add_separator()
        menu.add_command(label="Crear evento", command=crear_evento)
        menu.add_command(label="Eliminar evento seleccionado", command=eliminar_evento)
    menu.add_separator()
    menu.add_command(label="Cerrar sesión", command=lambda: globals().update(current_user=None) or login())
    menubar.add_cascade(label="Menú", menu=menu)
    root.config(menu=menubar)

    # Tabla
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    tree_global = ttk.Treeview(frame, columns=("ID","Título","Fecha","Hora","Lugar","Cupo","Inscritos"), show="headings", height=20)
    for col in tree_global["columns"]:
        tree_global.heading(col, text=col)
        tree_global.column(col, width=160, anchor="center")
    tree_global.pack(fill="both", expand=True)

    # Botones
    btns = tk.Frame(root)
    btns.pack(pady=10)
    tk.Button(btns, text="Actualizar", bg="#1976d2", fg="white", command=cargar_eventos).pack(side="left", padx=10)
    tk.Button(btns, text="Inscribirme", bg="#4caf50", fg="white", command=inscribirse).pack(side="left", padx=20)
    if current_user.rol == "organizador":
        tk.Button(btns, text="Crear Evento", bg="#FF5722", fg="white", command=crear_evento).pack(side="left", padx=10)
        tk.Button(btns, text="Eliminar Evento", bg="#f44336", fg="white", font=("bold", 12), command=eliminar_evento).pack(side="left", padx=10)

    cargar_eventos()

def cargar_eventos():
    if not tree_global: return
    for i in tree_global.get_children():
        tree_global.delete(i)
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, e.titulo, e.fecha, e.hora_inicio, e.lugar, e.capacidad_maxima, COALESCE(COUNT(i.id),0)
        FROM eventos e LEFT JOIN inscripciones i ON e.id = i.evento_id AND i.estado='confirmada'
        WHERE e.estado='publicado' GROUP BY e.id ORDER BY e.fecha
    """)
    for row in cur.fetchall():
        tree_global.insert("", "end", values=row)
    cur.close()
    conn.close()

def inscribirse():
    if current_user.rol != "usuario": 
        messagebox.showwarning("Rol", "Solo usuarios pueden inscribirse")
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
        messagebox.showinfo("Éxito", "¡Inscrito correctamente!")
        cargar_eventos()
    except:
        messagebox.showerror("Error", "Ya estás inscrito o no hay cupo")
    finally:
        cur.close()
        conn.close()

# ======================= INICIO =======================
root = tk.Tk()
root.title("Sistema de Eventos - UPSR")
root.geometry("1350x780")
root.configure(bg="#f0f8ff")

tk.Label(root, text="SISTEMA DE GESTIÓN\nde Inscripción y Asistencia a Eventos", font=("Helvetica", 26, "bold"), fg="#1B5E20", bg="#f0f8ff").pack(pady=130)
tk.Label(root, text="Oscar Alexandro Morales Galván - ISW-25", font=("Arial", 14), bg="#f0f8ff").pack(pady=10)
tk.Button(root, text="INICIAR SISTEMA", bg="#1B5E20", fg="white", font=("bold", 20), width=30, height=2, command=login).pack(pady=60)

root.mainloop()