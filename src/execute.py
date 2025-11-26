import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

try:
    from biblioteca import Biblioteca
    from usuario import Usuario, hash_password
    from libro import Libro
    
    bib = Biblioteca()
    current_user = None  # objeto Usuario autenticado
    
except Exception as e:
    print(f"Error de inicialización: {e}")
    messagebox.showerror("Error", f"No se pudo inicializar la aplicación:\n{e}")
    sys.exit(1)

# Código de autorización para admin
ADMIN_AUTH_CODE = "admin123"  # Puedes cambiar este código

# --------------------------
# Funciones de la aplicación
# --------------------------

def login_inicial():
    """Solicita credenciales al iniciar la aplicación."""
    global current_user

    # Preguntar si el usuario ya tiene cuenta
    tiene = messagebox.askyesno("Bienvenido", "¿Tienes una cuenta en el sistema?")
    if tiene is None:
        salir()
        return

    if not tiene:
        # Permitir registro público (puede elegir rol, pero admin requiere código)
        try:
            u = registrar_usuario_publico()
            if u:
                # auto-login con el usuario creado
                current_user = u
                lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({current_user.role})")
                ajustar_menu_por_rol()
                listar_libros()
                return
            else:
                # Si el usuario canceló el registro, volver a preguntar inicio de sesión
                messagebox.showinfo("Info", "Registro cancelado. Se solicitará inicio de sesión.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el registro:\n{e}")

    # intentos iniciar sesión (3 intentos)
    for _ in range(3):
        login = simpledialog.askstring("Inicio de sesión", "Nombre de usuario:", parent=root)
        if login is None:
            salir()
            return
        pwd = simpledialog.askstring("Inicio de sesión", "Contraseña:", show='*', parent=root)
        if pwd is None:
            salir()
            return
        usuario = Usuario.autenticar(login.strip(), pwd)
        if usuario:
            current_user = usuario
            lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({current_user.role})")
            ajustar_menu_por_rol()
            listar_libros()
            return
        else:
            retry = messagebox.askretrycancel("Error", "Credenciales incorrectas. ¿Deseas intentar de nuevo?")
            if not retry:
                # dar opción para registrarse si no tiene cuenta
                want_reg = messagebox.askyesno("Registro", "¿Deseas registrarte ahora?")
                if want_reg:
                    try:
                        u = registrar_usuario_publico()
                        if u:
                            current_user = u
                            lbl_help.config(text=f"Usuario conectado: {current_user.nombre} ({current_user.role})")
                            ajustar_menu_por_rol()
                            listar_libros()
                            return
                    except Exception as e:
                        messagebox.showerror("Error", f"Error durante el registro:\n{e}")
                # si no se registra, seguir al siguiente intento (o salir si no quedan intentos)
    messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo.")
    salir()

def requiere_admin(func):
    """Decorador simple para funciones que requieren rol 'admin'."""
    def wrapper(*args, **kwargs):
        if current_user is None or current_user.role != 'admin':
            messagebox.showerror("Permisos", "Acción restringida: se requiere usuario admin.")
            return
        return func(*args, **kwargs)
    return wrapper

def verificar_codigo_admin():
    """Verifica el código de autorización para registrar admin."""
    codigo = simpledialog.askstring("Código de autorización", 
                                   "Ingrese el código para registrar un administrador:", 
                                   show='*', parent=root)
    return codigo == ADMIN_AUTH_CODE

def registrar_usuario_publico():
    """Permite registrar un usuario desde la pantalla de inicio (roles: cliente, bibliotecario, admin)."""
    nombre = simpledialog.askstring("Registrar usuario", "Nombre del usuario:", parent=root)
    if not nombre:
        return None
    
    # Permitir elegir rol en registro público
    role = simpledialog.askstring("Registrar usuario", "Rol (cliente/bibliotecario/admin):", initialvalue="cliente", parent=root)
    if role is None:
        return None
    role = role.strip().lower()
    if role not in ('cliente', 'bibliotecario', 'admin'):
        messagebox.showwarning("Rol inválido", "Rol inválido. Se usará 'cliente'.")
        role = 'cliente'

    # Si el rol es admin, pedir código de autorización
    if role == 'admin':
        if not verificar_codigo_admin():
            messagebox.showerror("Error", "Código de autorización incorrecto. No se puede registrar como admin.")
            return None
    
    pwd = simpledialog.askstring("Registrar usuario", "Contraseña (dejar vacío = sin contraseña):", show='*', parent=root)
    
    # Crear usuario en la BD
    try:
        u = Usuario.crear(nombre.strip(), role, pwd)
        messagebox.showinfo("OK", f"Usuario registrado: {u.nombre} (id={u.id}, role={u.role})")
        return u
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar usuario: {e}")
        return None

# --- Registro / modificación / eliminación (admin) ---

@requiere_admin
def registrar_usuario():
    nombre = simpledialog.askstring("Registrar usuario", "Nombre del usuario:", parent=root)
    if not nombre:
        return
    role = simpledialog.askstring("Registrar usuario", "Rol (cliente/bibliotecario/admin):", initialvalue="cliente", parent=root)
    if not role:
        return
    
    # Verificar código si es admin
    if role.strip().lower() == 'admin':
        if not verificar_codigo_admin():
            messagebox.showerror("Error", "Código de autorización incorrecto.")
            return
    
    pwd = simpledialog.askstring("Registrar usuario", "Contraseña (opcional):", show='*', parent=root)
    try:
        u = Usuario.crear(nombre.strip(), role.strip().lower(), pwd)
        messagebox.showinfo("OK", f"Usuario registrado: {u.nombre} (id={u.id}, role={u.role})")
        listar_usuarios()
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")

@requiere_admin
def modificar_usuario():
    nombre = simpledialog.askstring("Modificar usuario", "Nombre del usuario a modificar:", parent=root)
    if not nombre:
        return
    usr = bib.buscar_usuario(nombre.strip())
    if usr is None:
        messagebox.showwarning("No encontrado", "Usuario no encontrado.")
        return
    
    nuevo_nombre = simpledialog.askstring("Modificar usuario", "Nuevo nombre:", initialvalue=usr.nombre, parent=root)
    nuevo_role = simpledialog.askstring("Modificar usuario", "Nuevo rol:", initialvalue=usr.role, parent=root)
    
    # Verificar código si se cambia a admin
    if nuevo_role.strip().lower() == 'admin' and usr.role != 'admin':
        if not verificar_codigo_admin():
            messagebox.showerror("Error", "Código de autorización incorrecto.")
            return
    
    nueva_pwd = simpledialog.askstring("Modificar usuario", "Nueva contraseña (vacío = sin cambio):", show='*', parent=root)
    try:
        conn = __import__('db_connection').get_conn()
        cur = conn.cursor()
        if nueva_pwd:
            from usuario import hash_password
            cur.execute("UPDATE usuarios SET nombre=%s, role=%s, password=%s WHERE id=%s",
                        (nuevo_nombre.strip(), nuevo_role.strip(), hash_password(nueva_pwd), usr.id))
        else:
            cur.execute("UPDATE usuarios SET nombre=%s, role=%s WHERE id=%s",
                        (nuevo_nombre.strip(), nuevo_role.strip(), usr.id))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("OK", "Usuario modificado.")
        listar_usuarios()
    except Exception as e:
        messagebox.showerror("Error", f"Error al modificar usuario:\n{e}")

@requiere_admin
def eliminar_usuario():
    nombre = simpledialog.askstring("Eliminar usuario", "Nombre del usuario a eliminar:", parent=root)
    if not nombre:
        return
    usr = bib.buscar_usuario(nombre.strip())
    if usr is None:
        messagebox.showwarning("No encontrado", "Usuario no encontrado.")
        return
    if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario '{usr.nombre}' (id={usr.id})?"):
        try:
            conn = __import__('db_connection').get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM usuarios WHERE id = %s", (usr.id,))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("OK", "Usuario eliminado.")
            listar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar usuario:\n{e}")

@requiere_admin
def registrar_libro():
    titulo = simpledialog.askstring("Registrar libro", "Título del libro:", parent=root)
    if not titulo:
        return
    autor = simpledialog.askstring("Registrar libro", "Autor del libro:", parent=root)
    if not autor:
        return
    try:
        l = bib.registrar_libro(titulo.strip(), autor.strip())
        messagebox.showinfo("OK", f"Libro registrado: {l.titulo} (id={l.id})")
        listar_libros()
    except Exception as e:
        messagebox.showerror("Error", f"Error al registrar libro:\n{e}")

@requiere_admin
def modificar_libro():
    titulo = simpledialog.askstring("Modificar libro", "Título del libro a modificar:", parent=root)
    if not titulo:
        return
    lib = bib.buscar_libro(titulo.strip())
    if lib is None:
        messagebox.showwarning("No encontrado", "Libro no encontrado.")
        return
    nuevo_titulo = simpledialog.askstring("Modificar libro", "Nuevo título:", initialvalue=lib.titulo, parent=root)
    nuevo_autor = simpledialog.askstring("Modificar libro", "Nuevo autor:", initialvalue=lib.autor, parent=root)
    try:
        conn = __import__('db_connection').get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE libros SET titulo=%s, autor=%s WHERE id=%s", (nuevo_titulo.strip(), nuevo_autor.strip(), lib.id))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("OK", "Libro modificado.")
        listar_libros()
    except Exception as e:
        messagebox.showerror("Error", f"Error al modificar libro:\n{e}")

@requiere_admin
def eliminar_libro():
    titulo = simpledialog.askstring("Eliminar libro", "Título del libro a eliminar:", parent=root)
    if not titulo:
        return
    lib = bib.buscar_libro(titulo.strip())
    if lib is None:
        messagebox.showwarning("No encontrado", "Libro no encontrado.")
        return
    if messagebox.askyesno("Confirmar", f"¿Eliminar el libro '{lib.titulo}' (id={lib.id})?"):
        try:
            conn = __import__('db_connection').get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM libros WHERE id = %s", (lib.id,))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("OK", "Libro eliminado.")
            listar_libros()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar libro:\n{e}")

# --- Listados / Prestamos (bibliotecario y admin) ---

def listar_usuarios():
    try:
        usuarios = bib.listar_usuarios()
        lb_output.delete(0, tk.END)
        if not usuarios:
            lb_output.insert(tk.END, "No hay usuarios registrados.")
            return
        lb_output.insert(tk.END, "Usuarios:")
        for u in usuarios:
            lb_output.insert(tk.END, f"  [{u.id}] {u.nombre} — {getattr(u, 'role', 'bibliotecario')}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar usuarios:\n{e}")

def listar_libros():
    try:
        libros = bib.listar_libros()
        lb_output.delete(0, tk.END)
        if not libros:
            lb_output.insert(tk.END, "No hay libros registrados.")
            return
        lb_output.insert(tk.END, "Libros:")
        for l in libros:
            status = "Disponible" if l.disponible else "Prestado"
            lb_output.insert(tk.END, f"  [{l.id}] {l.titulo} — {l.autor} ({status})")
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar libros:\n{e}")

def prestar_libro():
    if current_user is None:
        messagebox.showerror("Permisos", "Debe iniciar sesión.")
        return
    nombre = simpledialog.askstring("Prestar libro", "Nombre del usuario que toma el libro:", parent=root)
    if not nombre:
        return
    titulo = simpledialog.askstring("Prestar libro", "Título del libro:", parent=root)
    if not titulo:
        return
    try:
        msg = bib.prestar_libro(titulo.strip(), nombre.strip())
        messagebox.showinfo("Resultado", msg)
        listar_libros()
    except Exception as e:
        messagebox.showerror("Error", f"Error al prestar libro:\n{e}")

def devolver_libro():
    if current_user is None:
        messagebox.showerror("Permisos", "Debe iniciar sesión.")
        return
    nombre = simpledialog.askstring("Devolver libro", "Nombre del usuario que devuelve el libro:", parent=root)
    if not nombre:
        return
    titulo = simpledialog.askstring("Devolver libro", "Título del libro:", parent=root)
    if not titulo:
        return
    try:
        msg = bib.devolver_libro(titulo.strip(), nombre.strip())
        messagebox.showinfo("Resultado", msg)
        listar_libros()
    except Exception as e:
        messagebox.showerror("Error", f"Error al devolver libro:\n{e}")

def obtener_libros_prestados():
    """Modificada para que clientes solo vean sus propios libros"""
    if current_user is None:
        messagebox.showerror("Permisos", "Debe iniciar sesión.")
        return
    
    # Si es cliente, solo puede ver sus propios libros
    if current_user.role == 'cliente':
        usuario = current_user
    else:
        # Admin y bibliotecario pueden ver libros de cualquier usuario
        nombre = simpledialog.askstring("Libros prestados", "Nombre del usuario:", parent=root)
        if not nombre:
            return
        usuario = bib.buscar_usuario(nombre.strip())
        if usuario is None:
            messagebox.showwarning("No encontrado", "Usuario no encontrado.")
            return
    
    try:
        libros = usuario.obtener_libros_prestados()
        lb_output.delete(0, tk.END)
        lb_output.insert(tk.END, f"Libros prestados a {usuario.nombre}:")
        if not libros:
            lb_output.insert(tk.END, "  (No tiene libros prestados)")
            return
        for l in libros:
            lb_output.insert(tk.END, f"  [{l.id}] {l.titulo} — {l.autor}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al obtener libros prestados:\n{e}")

def salir():
    root.destroy()
    sys.exit(0)

def ajustar_menu_por_rol():
    """Habilita/deshabilita opciones del menú según el rol del usuario actual."""
    if current_user is None:
        # deshabilitar todo por seguridad
        acciones_menu.entryconfig("Registrar usuario", state="disabled")
        acciones_menu.entryconfig("Modificar usuario", state="disabled")
        acciones_menu.entryconfig("Eliminar usuario", state="disabled")
        acciones_menu.entryconfig("Registrar libro", state="disabled")
        acciones_menu.entryconfig("Modificar libro", state="disabled")
        acciones_menu.entryconfig("Eliminar libro", state="disabled")
        acciones_menu.entryconfig("Prestar libro", state="disabled")
        acciones_menu.entryconfig("Devolver libro", state="disabled")
        acciones_menu.entryconfig("Mostrar usuarios", state="disabled")
        acciones_menu.entryconfig("Mostrar libros", state="normal")
        acciones_menu.entryconfig("Obtener libros prestados (usuario)", state="disabled")
        return

    if current_user.role == 'admin':
        # Admin: habilitar todo
        acciones_menu.entryconfig("Registrar usuario", state="normal")
        acciones_menu.entryconfig("Modificar usuario", state="normal")
        acciones_menu.entryconfig("Eliminar usuario", state="normal")
        acciones_menu.entryconfig("Registrar libro", state="normal")
        acciones_menu.entryconfig("Modificar libro", state="normal")
        acciones_menu.entryconfig("Eliminar libro", state="normal")
        acciones_menu.entryconfig("Prestar libro", state="normal")
        acciones_menu.entryconfig("Devolver libro", state="normal")
        acciones_menu.entryconfig("Mostrar usuarios", state="normal")
        acciones_menu.entryconfig("Mostrar libros", state="normal")
        acciones_menu.entryconfig("Obtener libros prestados (usuario)", state="normal")
    else:
        # Bibliotecario o cliente: permisos limitados
        acciones_menu.entryconfig("Registrar usuario", state="disabled")
        acciones_menu.entryconfig("Modificar usuario", state="disabled")
        acciones_menu.entryconfig("Eliminar usuario", state="disabled")
        acciones_menu.entryconfig("Registrar libro", state="disabled")
        acciones_menu.entryconfig("Modificar libro", state="disabled")
        acciones_menu.entryconfig("Eliminar libro", state="disabled")
        # bibliotecario puede prestar/devolver; cliente solo listar y ver sus prestamos
        if current_user.role == 'bibliotecario':
            acciones_menu.entryconfig("Prestar libro", state="normal")
            acciones_menu.entryconfig("Devolver libro", state="normal")
            acciones_menu.entryconfig("Mostrar usuarios", state="normal")
            acciones_menu.entryconfig("Mostrar libros", state="normal")
            acciones_menu.entryconfig("Obtener libros prestados (usuario)", state="normal")
        else:  # cliente
            acciones_menu.entryconfig("Prestar libro", state="disabled")
            acciones_menu.entryconfig("Devolver libro", state="disabled")
            acciones_menu.entryconfig("Mostrar usuarios", state="disabled")
            acciones_menu.entryconfig("Mostrar libros", state="normal")
            acciones_menu.entryconfig("Obtener libros prestados (usuario)", state="normal")

# --------------------------
# Interfaz gráfica
# --------------------------

root = tk.Tk()
root.title("Biblioteca - Interfaz gráfica")
root.geometry("800x480")
root.minsize(700, 420)

# Configurar para que la ventana se mantenga enfocada
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)

# Menú principal
menubar = tk.Menu(root)

# Menú "Acciones" con las opciones
acciones_menu = tk.Menu(menubar, tearoff=0)
acciones_menu.add_command(label="Registrar usuario", command=registrar_usuario)
acciones_menu.add_command(label="Modificar usuario", command=modificar_usuario)
acciones_menu.add_command(label="Eliminar usuario", command=eliminar_usuario)
acciones_menu.add_separator()
acciones_menu.add_command(label="Registrar libro", command=registrar_libro)
acciones_menu.add_command(label="Modificar libro", command=modificar_libro)
acciones_menu.add_command(label="Eliminar libro", command=eliminar_libro)
acciones_menu.add_separator()
acciones_menu.add_command(label="Mostrar usuarios", command=listar_usuarios)
acciones_menu.add_command(label="Mostrar libros", command=listar_libros)
acciones_menu.add_separator()
acciones_menu.add_command(label="Prestar libro", command=prestar_libro)
acciones_menu.add_command(label="Devolver libro", command=devolver_libro)
acciones_menu.add_separator()
acciones_menu.add_command(label="Obtener libros prestados (usuario)", command=obtener_libros_prestados)
menubar.add_cascade(label="Acciones", menu=acciones_menu)

# Menú "Archivo" con Salir
archivo_menu = tk.Menu(menubar, tearoff=0)
archivo_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=archivo_menu)

root.config(menu=menubar)

# Frame principal para salida / resultados
frame_output = ttk.Frame(root, padding=(12, 12))
frame_output.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

lbl_output = ttk.Label(frame_output, text="Salida", font=("Segoe UI", 12, "bold"))
lbl_output.pack(anchor="w")

# Listbox con scrollbar para mostrar resultados
frame_list = ttk.Frame(frame_output)
frame_list.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

sb = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
lb_output = tk.Listbox(frame_list, yscrollcommand=sb.set, font=("Consolas", 10))
sb.config(command=lb_output.yview)
sb.pack(side=tk.RIGHT, fill=tk.Y)
lb_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Mensaje de ayuda inferior
lbl_help = ttk.Label(frame_output, text="Iniciando...", font=("Segoe UI", 9))
lbl_help.pack(anchor="w", pady=(8, 0))

# Al iniciar, pedir login
root.after(100, login_inicial)

root.mainloop()