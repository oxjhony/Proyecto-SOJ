import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import hashlib
import json
import threading
import queue

# Variables globales
usuarios = {}
usuario_actual = None
cola_explorador = queue.Queue()

# Función para cargar usuarios desde un archivo
def cargar_usuarios():
    global usuarios
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as file:
            usuarios = json.load(file)

# Función para guardar usuarios en un archivo
def guardar_usuarios():
    with open("usuarios.json", "w") as file:
        json.dump(usuarios, file)

# Función para cifrar contraseñas
def cifrar_contraseña(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para el inicio de sesión
def iniciar_sesion():
    global usuario_actual

    username = login_username.get()
    password = cifrar_contraseña(login_password.get())

    if username in usuarios and usuarios[username]['password'] == password:
        usuario_actual = username
        cargar_directorio_usuario()
        messagebox.showinfo("Inicio de sesión", f"Bienvenido, {usuario_actual}!")
        ventana_inicio_sesion.destroy()
        show_desktop()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# Función para el registro de nuevos usuarios
def registrar_usuario():
    global usuarios

    username = registro_username.get()
    password = cifrar_contraseña(registro_password.get())

    if username in usuarios:
        messagebox.showerror("Error", "El usuario ya existe.")
    else:
        usuarios[username] = {"password": password}
        guardar_usuarios()
        os.makedirs(f"./usuarios/{username}", exist_ok=True)
        messagebox.showinfo("Registro", "Usuario registrado con éxito.")
        ventana_registro.destroy()

# Función para cargar el directorio del usuario
def cargar_directorio_usuario():
    global usuario_actual

    if usuario_actual:
        user_directory = f"./usuarios/{usuario_actual}"
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)
        return user_directory

# Función para subir archivos en el directorio del usuario
def subir_archivo():
    user_directory = cargar_directorio_usuario()
    file_path = filedialog.askopenfilename(filetypes=[("Todos los archivos", "*.*")])

    if file_path:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(user_directory, file_name)

        try:
            with open(file_path, 'rb') as src_file:
                with open(dest_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
            update_directory_tree(tree, user_directory)
            messagebox.showinfo("Subida exitosa", f"Archivo '{file_name}' subido a tu directorio.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo subir el archivo: {e}")

# Función para mostrar la ventana de inicio de sesión
def mostrar_inicio_sesion():
    global ventana_inicio_sesion, login_username, login_password

    ventana_inicio_sesion = tk.Toplevel()
    ventana_inicio_sesion.title("Inicio de Sesión")
    ventana_inicio_sesion.geometry("300x200")

    tk.Label(ventana_inicio_sesion, text="Usuario").pack(pady=5)
    login_username = tk.Entry(ventana_inicio_sesion)
    login_username.pack(pady=5)

    tk.Label(ventana_inicio_sesion, text="Contraseña").pack(pady=5)
    login_password = tk.Entry(ventana_inicio_sesion, show="*")
    login_password.pack(pady=5)

    tk.Button(ventana_inicio_sesion, text="Iniciar Sesión", command=iniciar_sesion).pack(pady=10)

# Función para mostrar la ventana de registro
def mostrar_registro():
    global ventana_registro, registro_username, registro_password

    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registro")
    ventana_registro.geometry("300x200")

    tk.Label(ventana_registro, text="Nuevo Usuario").pack(pady=5)
    registro_username = tk.Entry(ventana_registro)
    registro_username.pack(pady=5)

    tk.Label(ventana_registro, text="Contraseña").pack(pady=5)
    registro_password = tk.Entry(ventana_registro, show="*")
    registro_password.pack(pady=5)

    tk.Button(ventana_registro, text="Registrar", command=registrar_usuario).pack(pady=10)

# Función para actualizar el contenido del árbol de directorios
def update_directory_tree(tree, path):
    tree.delete(*tree.get_children())
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                tree.insert('', 'end', text=item, values=[item_path])
            else:
                tree.insert('', 'end', text=item, values=[item_path])
    except PermissionError:
        pass

# Función para la pantalla de bienvenida y menú
def show_desktop():
    window = tk.Tk()
    window.title("Simulación de Escritorio Windows")
    window.geometry("800x600")

    tk.Label(window, text=f"Bienvenido, {usuario_actual}", font=("Arial", 16)).pack(pady=10)

    # Crear marco para el explorador de archivos
    explorer_frame = tk.Frame(window)
    explorer_frame.pack(fill="both", expand=True, padx=10, pady=10)

    global tree
    tree = ttk.Treeview(explorer_frame, columns=("fullpath",), show="tree")
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    user_directory = cargar_directorio_usuario()
    update_directory_tree(tree, user_directory)

    # Botón para subir archivos
    upload_button = tk.Button(explorer_frame, text="Subir Archivo", command=subir_archivo, bg="blue", fg="white", font=("Arial", 10))
    upload_button.pack(side="bottom", pady=10)

    window.mainloop()

# Cargar usuarios al inicio
cargar_usuarios()

# Ventana inicial para elegir entre Iniciar Sesión y Registrarse
root = tk.Tk()
root.title("Sistema de Escritorio Simulado")
root.geometry("300x150")

tk.Button(root, text="Iniciar Sesión", command=mostrar_inicio_sesion).pack(pady=10)
tk.Button(root, text="Registrar", command=mostrar_registro).pack(pady=10)

root.mainloop()
