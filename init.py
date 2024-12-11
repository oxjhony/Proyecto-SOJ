import tkinter as tk
import time
import os
import threading
import queue
from tkinter import ttk, filedialog, messagebox
import os
import hashlib
import json
import threading
import queue
import requests
from threading import Thread, Event
from PIL import Image, ImageTk
import pygame
import random
from tkhtmlview import HTMLLabel
from tkinterweb import HtmlFrame
import sys
import webbrowser
#import webview 
import cv2
from ffpyplayer.player import MediaPlayer

import math

class Auth:
    def __init__(self):
        self.usuarios = {}
        self.usuario_actual = None
        self.cargar_usuarios()


    def cargar_usuarios(self):
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r") as file:
                self.usuarios = json.load(file)

    def guardar_usuarios(self):
        #Si usuarios.json no existe, se crea


        if not os.path.exists("usuarios.json"):
            with open("usuarios.json", "w") as file:
                json.dump({}, file)


        else:  
            with open("usuarios.json", "w") as file:
                json.dump(self.usuarios, file)
       




    def cifrar_contraseña(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def iniciar_sesion(self, username, password):
        password_hash = self.cifrar_contraseña(password)
        if username in self.usuarios and self.usuarios[username]['password'] == password_hash:
            self.usuario_actual = username
            return True
        return False


    def registrar_usuario(self, username, password, admin=False):
        if username in self.usuarios:
            return False
        self.usuarios[username] = {
            "password": self.cifrar_contraseña(password),
            "admin": admin  # Añadimos el rol de administrador
        }
        self.guardar_usuarios()

        # Crear la carpeta del usuario y subcarpetas
        user_directory = f"./usuarios/{username}"
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)

        carpetas = ["Documentos", "Descargas", "Música", "Videos", "Imágenes"]
        for carpeta in carpetas:
            carpeta_path = os.path.join(user_directory, carpeta)
            if not os.path.exists(carpeta_path):
                os.makedirs(carpeta_path)

        return True

    def cargar_directorio_usuario(self):
        """Devuelve el directorio raíz del usuario actual."""
        if self.usuario_actual:
            user_directory = f"./usuarios/{self.usuario_actual}"
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
            return user_directory
        return None

    def es_admin(self):
        """Devuelve True si el usuario actual es administrador, de lo contrario False."""
        try:
            if self.usuario_actual:
                return self.usuarios[self.usuario_actual].get("admin", False)
        except Exception:
            return False
        return False  # Por defecto, se devuelve False si ocurre un error


class FileExplorer:
    def __init__(self, frame, auth):
        self.frame = frame
        self.auth = auth
        self.tree = None


    def cargar_explorador_usuario(self):
        user_directory = self.auth.cargar_directorio_usuario()
        if user_directory:
            self._limpiar_frame()


            top_frame = tk.Frame(self.frame, bg="lightgray")
            top_frame.pack(fill="x")


            path_label = tk.Label(self.frame, text=user_directory, anchor="w")
            path_label.pack(fill="x", padx=10, pady=5)


            self.tree = ttk.Treeview(self.frame, columns=("fullpath",), show="tree")
            self.tree.pack(fill="both", expand=True, padx=10, pady=5)


            self.update_directory_tree(user_directory)


            upload_button = tk.Button(self.frame, text="Subir Archivo", command=self.subir_archivo, bg="blue", fg="white", font=("Arial", 10))
            upload_button.pack(side="bottom", pady=5)


    def _limpiar_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


    def update_directory_tree(self, path):
        self.tree.delete(*self.tree.get_children())
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                self.tree.insert('', 'end', text=item, values=[item_path])
        except PermissionError:
            pass


    def subir_archivo(self):
        user_directory = self.auth.cargar_directorio_usuario()
        file_path = filedialog.askopenfilename(filetypes=[("Todos los archivos", "*.*")])


        if file_path:
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(user_directory, file_name)


            try:
                with open(file_path, 'rb') as src_file:
                    with open(dest_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                self.update_directory_tree(user_directory)
                messagebox.showinfo("Subida exitosa", f"Archivo '{file_name}' subido a tu directorio.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo subir el archivo: {e}")




class DesktopApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Simulación de Escritorio Windows")
        self.window.geometry("800x600")
        self.window.config(bg="lightblue")




        self.auth = Auth()
       


        self.procesos_activos = {}
        self.cola_calculadora = queue.Queue()
        self.cola_hora = queue.Queue()
        self.cola_explorador = queue.Queue()
        self.cola_tabla_control = queue.Queue()


        self.procesos_activos = {}
        self.cola_calculadora = queue.Queue()
        self.cola_hora = queue.Queue()
        # Crear las ventanas y frames necesarios
        self.create_auth_frame()  # Añadir este frame para autenticación
        self.create_clock_frame()
        self.create_taskbar()
        self.create_menu()
        self.create_task_manager_frame()  # Añadir esta línea
        self.create_explorer_frame()
        self.create_calculator_frame()
        self.create_hora_frame()
                # Inicializar el atributo chrome_frame como None
        self.browser_frame = None


        self.create_welcome_screen()
       
        self.message_label = tk.Label(self.window, text="", font=("Arial", 12), bg="white", fg="green")
        self.message_label.pack(pady=10)








        # Iniciar el reloj
        self.update_clock()


   




        self.window.mainloop()
       # Crear etiqueta para mostrar mensajes







    def actualizar_procesos_activos(self):
        # Método para actualizar la lista de procesos activos en el Administrador de Tareas
        if hasattr(self, 'task_manager'):
            self.task_manager.mostrar()
   


    def _limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()


    def create_auth_frame(self):
        self.auth_frame = tk.Frame(self.window, bg="white")
        self.auth_frame.pack(fill="both", expand=True)


    def create_clock_frame(self):
        """Crea un marco para mostrar el reloj en la esquina inferior derecha."""
        self.clock_frame = tk.Frame(self.window, bg="lightblue")
        self.clock_frame.place(relx=1.0, rely=1.0, anchor="se")  # Posición inferior derecha
        self.clock_label = tk.Label(self.clock_frame, font=("Arial", 12), bg="gray", fg="white")
        self.clock_label.pack(padx=5, pady=5)


    def update_clock(self):
        """Actualiza el reloj en la esquina inferior derecha cada segundo."""
        current_time = time.strftime('%I:%M:%S %p')
        self.clock_label.config(text=current_time)
        self.window.after(1000, self.update_clock)  # Actualizar cada segundo


    def mostrar_inicio_sesion(self):
        # Limpiar el marco de autenticación antes de mostrar el formulario de inicio de sesión
        self._limpiar_frame(self.auth_frame)


        tk.Label(self.auth_frame, text="Usuario").pack(pady=5)
        login_username = tk.Entry(self.auth_frame)
        login_username.pack(pady=5)


        tk.Label(self.auth_frame, text="Contraseña").pack(pady=5)
        login_password = tk.Entry(self.auth_frame, show="*")
        login_password.pack(pady=5)


        def intentar_iniciar_sesion():
            if not self.message_label.winfo_exists():
                return  # Evitar errores si la ventana ha sido destruida


            username = login_username.get()
            password = login_password.get()
            if self.auth.iniciar_sesion(username, password):
                self.message_label.config(text=f"Bienvenido, {username}!", fg="green")
                self.auth_frame.pack_forget()  # Ocultar el marco de autenticación
                self.show_desktop()  # Mostrar el escritorio
                self.window.after(4000, self.message_label.pack_forget)  # Limpiar el mensaje después de 4 segundos
           
            else:
                self.message_label.config(text="Usuario o contraseña incorrectos.", fg="red")
                self.window.after(4000, self.limpiar_mensaje)  # Limpiar el mensaje después de 4 segundos
               




        tk.Button(self.auth_frame, text="Iniciar Sesión", command=intentar_iniciar_sesion).pack(pady=10)


        def _limpiar_frame(self, frame):
            for widget in frame.winfo_children():
                widget.destroy()


       
        def limpiar_mensaje(self):
            """Función para limpiar el mensaje en la etiqueta después de 4 segundos."""
            self.message_label.config(text="")


           
    def limpiar_mensaje(self):
        """Función para limpiar el mensaje en la etiqueta después de 4 segundos."""
        self.message_label.config(text="")






    def create_welcome_screen(self):
        # Limpiar todos los frames existentes antes de mostrar la pantalla de bienvenida
        self._limpiar_frame(self.auth_frame)

        # Crear la ventana de bienvenida
        self.welcome_frame = tk.Frame(self.window, bg="white")
        self.welcome_frame.pack(fill="both", expand=True)

        # Agregar el texto "Bienvenido"
        welcome_label = tk.Label(self.welcome_frame, text="Bienvenido", font=("Arial", 24), bg="white")
        welcome_label.pack(pady=20)

        # Mostrar la imagen del logo correctamente
        logo_path = os.path.join(os.getcwd(), "images", "s1.png")  # Asegúrate de que la ruta sea correcta
        if os.path.exists(logo_path):
            logo = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(self.welcome_frame, image=logo, bg="white")
            logo_label.image = logo  # Mantener una referencia para evitar que se recolecte
            logo_label.pack(pady=10)
        else:
            logo_label = tk.Label(self.welcome_frame, text="Logo no encontrado", bg="white", font=("Arial", 14), fg="red")
            logo_label.pack(pady=10)

        # Botones para Iniciar Sesión y Registrarse
        login_button = tk.Button(
            self.welcome_frame, text="Iniciar Sesión", command=self.mostrar_inicio_sesion,
            font=("Arial", 14), bg="blue", fg="white"
        )
        login_button.pack(pady=10)

        register_button = tk.Button(
            self.welcome_frame, text="Registrar", command=self.mostrar_registro,
            font=("Arial", 14), bg="green", fg="white"
        )
        register_button.pack(pady=10)

    def mostrar_registro(self):
        # Limpiar el marco actual antes de mostrar el formulario de registro
        self._limpiar_frame(self.auth_frame)

        # Título de la ventana
        tk.Label(self.auth_frame, text="Registrar Usuario", font=("Arial", 18), bg="white").pack(pady=10)

        # Campo para ingresar nombre de usuario
        tk.Label(self.auth_frame, text="Nuevo Usuario:", bg="white").pack(pady=5)
        registro_username = tk.Entry(self.auth_frame)
        registro_username.pack(pady=5)

        # Campo para ingresar contraseña
        tk.Label(self.auth_frame, text="Contraseña:", bg="white").pack(pady=5)
        registro_password = tk.Entry(self.auth_frame, show="*")
        registro_password.pack(pady=5)

        # Checkbox para definir si el usuario es administrador
        is_admin = tk.BooleanVar()
        admin_checkbox = tk.Checkbutton(
            self.auth_frame,
            text="Administrador",
            variable=is_admin,
            bg="white"
        )
        admin_checkbox.pack(pady=5)

        # Mensaje de error o éxito
        message_label = tk.Label(self.auth_frame, text="", bg="white", fg="red", font=("Arial", 12))
        message_label.pack(pady=5)

        # Función para intentar registrar un usuario
        def intentar_registrar_usuario():
            username = registro_username.get().strip()
            password = registro_password.get().strip()

            if not username or not password:
                message_label.config(text="Todos los campos son obligatorios.")
                return

            if self.auth.registrar_usuario(username, password, is_admin.get()):
                message_label.config(text="Usuario registrado con éxito.", fg="green")
                self.window.after(2000, self.mostrar_inicio_sesion)  # Ir al login tras éxito
            else:
                message_label.config(text="El usuario ya existe.", fg="red")

        # Botón para registrar
        tk.Button(
            self.auth_frame,
            text="Registrar",
            command=intentar_registrar_usuario,
            bg="green",
            fg="white",
            font=("Arial", 12)
        ).pack(pady=10)

        # Botón para ir al inicio de sesión
        tk.Button(
            self.auth_frame,
            text="Iniciar Sesión",
            command=self.mostrar_inicio_sesion,
            bg="blue",
            fg="white",
            font=("Arial", 12)
        ).pack(pady=5)





    def create_taskbar(self):
        self.taskbar = tk.Frame(self.window, bg="gray", height=40)
        self.start_button = tk.Button(self.taskbar, text="Inicio", command=self.toggle_menu, bg="lightgray")
        self.start_button.pack(side="left", padx=5)
        self.clock_label = tk.Label(self.taskbar, font=("Arial", 12), bg="gray", fg="white")
        self.clock_label.pack(side="right", padx=10)


    def create_menu(self):
        self.menu_frame = tk.Frame(self.window, bg="lightgray", width=200, height=300)
        programs = ["Calculadora", "Explorador","Administrador de Tareas","Musica", "Editor de Texto","Horarios", "Visualizador", "Culebra","Navegador","Apagar","Video"]
        for program in programs:
            if program == "Apagar":
                button = tk.Button(self.menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=self.apagar)
            elif program == "Administrador de Tareas":
                button = tk.Button(self.menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=self.toggle_task_manager)
            else:
                button = tk.Button(self.menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=lambda p=program: self.abrir_aplicacion(p))
            button.pack(pady=2)

    def abrir_navegador(self):
        """Incrusta un navegador en una subventana dentro de la aplicación."""
        if self.browser_frame:
            # Si el navegador ya está abierto, traerlo al frente
            self.browser_frame.lift()
            return

        # Crear el marco para el navegador
        self.browser_frame = tk.Frame(self.window, bg="white")
        self.browser_frame.pack(fill="both", expand=True)

        # Botón para cerrar el navegador
        close_button = tk.Button(
            self.browser_frame,
            text="Cerrar Navegador",
            bg="red",
            fg="white",
            command=self.cerrar_navegador
        )
        close_button.pack(anchor="ne", pady=5, padx=5)

        # Crear el navegador usando tkinterweb
        html_view = HtmlFrame(self.browser_frame)
        html_view.load_website("https://www.google.com")
        html_view.pack(fill="both", expand=True)

    def cerrar_navegador(self):
        """Cierra el navegador embebido."""
        if self.browser_frame:
            self.browser_frame.destroy()
            self.browser_frame = None

    def create_task_manager_frame(self):
        self.task_manager_frame = tk.Frame(self.window, bg="lightgray", width=250, height=600)
        self.task_manager = TaskManager(self.task_manager_frame, self.procesos_activos)
       
    def create_explorer_frame(self):
        self.explorer_frame = tk.Frame(self.window, bg="lightgray", width=300, height=400)


    def create_hora_frame(self):
        self.hora_frame = tk.Frame(self.window, bg="lightgray", width=300, height=400)



    def create_calculator_frame(self):
        self.calculator_frame = tk.Frame(self.window, bg="lightgray", width=300, height=400)


    def show_desktop(self):
        self.welcome_frame.pack_forget()
        self.taskbar.pack(side="bottom", fill="x")
        self.file_explorer = FileExplorer(self.calculator_frame, self.auth)
        self.file_explorer.cargar_explorador_usuario()


    def toggle_menu(self):
        if self.menu_frame.winfo_ismapped():
            self.menu_frame.pack_forget()
        else:
            self.menu_frame.pack(side="left", anchor="sw", padx=1, pady=(0, 1))


    def abrir_aplicacion(self, nombre_aplicacion):
        if nombre_aplicacion == "Calculadora":
            CalculatorApp(self)
        elif nombre_aplicacion == "Explorador":
            FileExplorerApp(self)
        elif nombre_aplicacion == "Horarios":
            WorldTimeApp(self)
        elif nombre_aplicacion == "Editor de Texto":
            TextApp(self)
        elif nombre_aplicacion == "Musica":
            MusicPlayerApp(self)
        elif nombre_aplicacion == "Visualizador":
            ImageViewerApp(self)
        elif nombre_aplicacion == "Culebra":
            SnakeApp(self)
        elif nombre_aplicacion == "Navegador":
            BrowserApp(self) 
        elif nombre_aplicacion == "Video":
            VideoPlayerApp(self)
        elif nombre_aplicacion == "Apagar":
            self.apagar()


    def toggle_task_manager(self):
        if self.task_manager_frame.winfo_ismapped():
            self.task_manager.ocultar()
        else:
            self.task_manager_frame.pack(side="right", fill="y", padx=5, pady=5)
            self.task_manager.mostrar()


    def update_clock(self):
        current_time = time.strftime('%I:%M %p')
        self.clock_label.config(text=current_time)
        self.window.after(1000, self.update_clock)


    def apagar(self):
        self.window.destroy()


class CalculatorApp:
    instance_counter = 0  # Contador estático para generar identificadores únicos

    def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        self.cola_calculadora = queue.Queue()
        self.calculator_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=300, height=400)
        self.calculator_frame.pack_propagate(False)
        self.calculator_frame.pack(padx=10, pady=10)

        # Asignar un identificador único a esta instancia
        CalculatorApp.instance_counter += 1
        self.instance_id = f"Calculadora {CalculatorApp.instance_counter}"
        

        self.procesos_activos = self.desktop_app.procesos_activos
        self.mostrar_calculadora()

    def mostrar_calculadora(self):
        # Limpiar el marco antes de mostrar la calculadora
        for widget in self.calculator_frame.winfo_children():
            widget.destroy()

        # Crear el frame superior con el botón de cerrar
        top_frame = tk.Frame(self.calculator_frame, bg="lightgray")
        top_frame.grid(row=0, column=0, columnspan=8, sticky="we")
        close_button = tk.Button(
            top_frame, text="X", command=self.cerrar_calculadora, bg="red", fg="white", font=("Arial", 12, "bold")
        )
        close_button.pack(side="right")

        # Entrada de texto de la calculadora
        self.entry = tk.Entry(
            self.calculator_frame, width=35, font=("Arial", 18), borderwidth=2, relief="solid", justify="right"
        )
        self.entry.grid(row=1, column=0, columnspan=8, pady=10)

        # Botones de la calculadora
        button_texts = [
            ('7', '8', '9', '/', 'sqrt', 'sin', 'cos', 'tan'),
            ('4', '5', '6', '*', '^2', 'log', 'exp', 'pi'),
            ('1', '2', '3', '-', '^', '(', ')', 'e'),
            ('0', '.', '=', '+', 'AC', 'C', '%', '1/x')
        ]
        row_val = 2
        for row in button_texts:
            col_val = 0
            for text in row:
                action = lambda x=text: self.process_button(x)
                b = tk.Button(self.calculator_frame, text=text, width=5, height=2, command=action, font=("Arial", 14))
                b.grid(row=row_val, column=col_val, padx=5, pady=5)
                col_val += 1
            row_val += 1

        # Calcular y registrar memoria utilizada
        memoria_usada = self.calcular_memoria_calculadora()
        hilo = threading.Thread(target=self.hilo_calculadora, args=(self.cola_calculadora,), daemon=True)
        hilo.start()
        self.procesos_activos[self.instance_id] = {
            "frame": self.calculator_frame,
            "memoria": memoria_usada,
            "hilo": hilo,
            "cola": self.cola_calculadora,
        }
        self.desktop_app.actualizar_procesos_activos()

    def process_button(self, value):
        if value == '=':
            self.calcular_resultado()
        elif value == 'AC':
            self.entry.delete(0, tk.END)
        elif value == 'C':
            self.entry.delete(len(self.entry.get()) - 1, tk.END)
        elif value == 'sqrt':
            self.entry.insert(tk.END, '**0.5')
        elif value == '^2':
            self.entry.insert(tk.END, '**2')
        elif value == '^':
            self.entry.insert(tk.END, '**')
        elif value == 'pi':
            self.entry.insert(tk.END, str(math.pi))
        elif value == 'e':
            self.entry.insert(tk.END, str(math.e))
        elif value == 'sin':
            self.entry.insert(tk.END, 'math.sin(')
        elif value == 'cos':
            self.entry.insert(tk.END, 'math.cos(')
        elif value == 'tan':
            self.entry.insert(tk.END, 'math.tan(')
        elif value == 'log':
            self.entry.insert(tk.END, 'math.log(')
        elif value == 'exp':
            self.entry.insert(tk.END, 'math.exp(')
        elif value == '1/x':
            self.entry.insert(tk.END, '**-1')
        else:
            self.entry.insert(tk.END, value)

    def calcular_resultado(self):
        try:
            result = eval(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, "Error")

    def cerrar_calculadora(self):
        self.cola_calculadora.put("cerrar")
        self.calculator_frame.pack_forget()
        if self.instance_id in self.procesos_activos:
            del self.procesos_activos[self.instance_id]
        self.desktop_app.actualizar_procesos_activos()

    def calcular_memoria_calculadora(self):
        """Calcula la memoria utilizada por la calculadora."""
        memoria_base = 20
        memoria_adicional = len(self.calculator_frame.winfo_children()) * 2
        return memoria_base + memoria_adicional

    def hilo_calculadora(self, cola):
        """Hilo para manejar mensajes de la cola."""
        while True:
            mensaje = cola.get()
            if mensaje == "cerrar":
                break












class FileExplorerApp:
    instance_counter = 0  # Contador estático para generar identificadores únicos

    def __init__(self, desktop_app, initial_path=None):
        self.desktop_app = desktop_app
        self.explorer_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=600, height=400)
        self.explorer_frame.pack_propagate(False)
        self.explorer_frame.pack(padx=10, pady=10)

        self.current_path = initial_path or self.desktop_app.auth.cargar_directorio_usuario()

        # Asignar un identificador único a esta instancia
        FileExplorerApp.instance_counter += 1
        self.instance_id = f"Explorador {FileExplorerApp.instance_counter}"

        # Cola y evento para controlar el hilo
        self.evento_cierre = threading.Event()
        self.cola = queue.Queue()

        self.setup_ui()
        self.display_directory(self.current_path)

        # Registrar el proceso en el Administrador de Tareas
        memoria_usada = self.calcular_memoria_explorador()
        self.hilo = threading.Thread(target=self.hilo_explorador, daemon=True)
        self.hilo.start()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.explorer_frame,
            "memoria": memoria_usada,
            "hilo": self.hilo,
            "cola": self.cola,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado y botón cerrar
        top_frame = tk.Frame(self.explorer_frame, bg="lightgray")
        top_frame.pack(fill="x")

        close_button = tk.Button(
            top_frame, text="X", command=self.close_explorer, bg="red", fg="white", font=("Arial", 12, "bold")
        )
        close_button.pack(side="right")

        back_button = tk.Button(
            top_frame, text="←", command=self.go_back, bg="blue", fg="white", font=("Arial", 12, "bold")
        )
        back_button.pack(side="left", padx=5)

        upload_button = tk.Button(
            top_frame, text="Subir Archivo", command=self.upload_file, bg="green", fg="white", font=("Arial", 12, "bold")
        )
        upload_button.pack(side="left", padx=5)

        # Canvas y scrollbar
        self.canvas = tk.Canvas(self.explorer_frame, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.explorer_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Limitar el área visible del slider
        self.inner_frame.bind("<Configure>", lambda e: self.update_scroll_region())

    def update_scroll_region(self):
        """Actualiza la región de desplazamiento del canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def display_directory(self, path):
        """Muestra el contenido del directorio."""
        # Verifica restricciones para usuarios no administradores
        if not self.desktop_app.auth.es_admin():
            base_path = self.desktop_app.auth.cargar_directorio_usuario()
            if not path.startswith(base_path):
                messagebox.showwarning("Acceso Restringido", "No tienes permiso para acceder a este directorio.")
                return

        # Limpiar contenido previo
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.current_path = path

        try:
            items = os.listdir(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se puede acceder al directorio: {e}")
            return

        row, col = 0, 0
        max_columns = 4

        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                self.create_icon(item, item_path, row, col, icon_type="folder")
            elif os.path.isfile(item_path):
                ext = os.path.splitext(item)[-1].lower()
                if ext in [".png", ".jpg", ".bmp"]:
                    self.create_icon(item, item_path, row, col, icon_type="image")
                elif ext in [".mp3", ".wav", ".ogg"]:
                    self.create_icon(item, item_path, row, col, icon_type="music")
                elif ext == ".txt":
                    self.create_icon(item, item_path, row, col, icon_type="text")
                elif ext in [".mp4", ".avi", ".mkv"]:
                    self.create_icon(item, item_path, row, col, icon_type="video")

            col += 1
            if col >= max_columns:
                col = 0
                row += 1

    def create_icon(self, name, path, row, col, icon_type):
        """Crea un icono representando un archivo o carpeta."""
        frame = tk.Frame(self.inner_frame, bg="white", padx=5, pady=5)
        frame.grid(row=row, column=col, padx=10, pady=10)

        icon_dict = {
            "folder": "📁",
            "image": "🖼️",
            "music": "🎵",
            "text": "📄",
            "video": "🎥",
        }

        icon = tk.Label(frame, text=icon_dict.get(icon_type, "❓"), font=("Arial", 24), bg="white")
        icon.pack()

        label = tk.Label(frame, text=name, font=("Arial", 10), bg="white", wraplength=100, anchor="center")
        label.pack()

        frame.bind("<Button-1>", lambda e: self.open_item(path, icon_type))
        icon.bind("<Button-1>", lambda e: self.open_item(path, icon_type))
        label.bind("<Button-1>", lambda e: self.open_item(path, icon_type))

    def open_item(self, path, item_type):
        """Abre el archivo o carpeta."""
        if item_type == "folder":
            self.display_directory(path)
        elif item_type == "image":
            ImageViewerApp(self.desktop_app, path=path)
        elif item_type == "music":
            MusicPlayerApp(self.desktop_app, path=path)
        elif item_type == "text":
            TextApp(self.desktop_app, file_path=path)
        elif item_type == "video":
            VideoPlayerApp(self.desktop_app, video_path=path)

    def go_back(self):
        """Regresa al directorio anterior."""
        parent_dir = os.path.dirname(self.current_path)
        base_path = self.desktop_app.auth.cargar_directorio_usuario()

        if not self.desktop_app.auth.es_admin() and not parent_dir.startswith(base_path):
            messagebox.showwarning("Acceso Restringido", "No puedes retroceder más allá de tu directorio base.")
            return

        if parent_dir and parent_dir != self.current_path:
            self.display_directory(parent_dir)

    def upload_file(self):
        """Sube un archivo al directorio actual."""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                dest_path = os.path.join(self.current_path, os.path.basename(file_path))
                with open(file_path, "rb") as src_file:
                    with open(dest_path, "wb") as dest_file:
                        dest_file.write(src_file.read())
                self.display_directory(self.current_path)
                messagebox.showinfo("Éxito", f"Archivo '{os.path.basename(file_path)}' subido correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo subir el archivo: {e}")

    def calcular_memoria_explorador(self):
        """Calcula la memoria usada por el explorador."""
        memoria_base = 50
        num_items = len(self.inner_frame.winfo_children()) * 2
        return memoria_base + num_items

    def hilo_explorador(self):
        """Ejecuta un hilo para escuchar eventos de cierre."""
        while not self.evento_cierre.is_set():
            try:
                mensaje = self.cola.get(timeout=0.1)
                if mensaje == "cerrar":
                    break
            except queue.Empty:
                continue

    def close_explorer(self):
        """Cierra el explorador de archivos."""
        self.evento_cierre.set()
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.explorer_frame.pack_forget()
        self.desktop_app.actualizar_procesos_activos()











class TaskManager:
    def __init__(self, frame, procesos_activos):
        self.frame = frame
        self.procesos_activos = procesos_activos


    def mostrar(self):
        self._limpiar_frame()


        tk.Label(self.frame, text="Procesos Activos:", font=("Arial", 12, "bold")).pack(pady=5)


        for proceso, datos in self.procesos_activos.items():
            proceso_frame = tk.Frame(self.frame, bg="lightgray")
            proceso_frame.pack(fill="x", padx=10, pady=2)


            tk.Label(proceso_frame, text=f"{proceso} - {datos['memoria']} MB", font=("Arial", 10)).pack(side="left", padx=5)


            cerrar_button = tk.Button(proceso_frame, text="Cerrar", command=lambda p=proceso: self.cerrar_proceso(p), bg="red", fg="white", font=("Arial", 10, "bold"))
            cerrar_button.pack(side="right", padx=5)


        cerrar_button = tk.Button(self.frame, text="Cerrar Administrador", command=self.ocultar, bg="gray")
        cerrar_button.pack(pady=10)


    def _limpiar_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


    def cerrar_proceso(self, proceso):
        if proceso in self.procesos_activos:
            proceso_data = self.procesos_activos[proceso]
            frame = proceso_data["frame"]
            
            # Verificar si existe "hilo" y "cola"
            hilo = proceso_data.get("hilo", None)
            cola = proceso_data.get("cola", None)
            
            if frame:
                frame.pack_forget()
            
            # Cerrar cola e hilo si existen
            if cola:
                cola.put("cerrar")
            if hilo and hilo.is_alive():
                hilo.join(timeout=1)
            
            # Eliminar proceso activo
            del self.procesos_activos[proceso]
            self.mostrar()


    def ocultar(self):
        self.frame.pack_forget()

class WorldTimeApp:
    def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        self.hora_frame = desktop_app.hora_frame
        self.procesos_activos = desktop_app.procesos_activos
        self.stopped = Event()  # Señal para detener hilos
        self.threads = []  # Lista para rastrear todos los hilos activos
        self.mostrar_hora_mundial()

    def mostrar_hora_mundial(self):
        # Limpiar cualquier widget previo en el frame
        for widget in self.hora_frame.winfo_children():
            widget.destroy()

        self.hora_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame superior con botón de cerrar
        top_frame = tk.Frame(self.hora_frame, bg="lightgray")
        top_frame.pack(fill="x")
        close_button = tk.Button(
            top_frame, text="X", command=self.cerrar_hora_mundial,
            bg="red", fg="white", font=("Arial", 12, "bold")
        )
        close_button.pack(side="right")

        # Etiqueta de bienvenida
        message_label = tk.Label(self.hora_frame, text="¡Bienvenido a la Aplicación de Hora Mundial!", font=("Arial", 16))
        message_label.pack(pady=20)

        # Ciudades a mostrar
        self.cities = ["America/Grand_Turk", "America/Argentina/Buenos_Aires", "Europe/Madrid", "Asia/Tokyo", "Australia/Sydney"]
        self.labels = {}

        # Crear etiquetas para cada ciudad
        for city in self.cities:
            self.labels[city] = tk.Label(self.hora_frame, text=f"Cargando hora para {city.split('/')[1]}...", bg="lightgray")
            self.labels[city].pack()

        # Inicia el hilo principal para actualizar los tiempos
        main_thread = Thread(target=self.update_times, daemon=True)
        self.threads.append(main_thread)
        main_thread.start()

        # Registrar proceso en la lista de procesos activos
        memoria_usada = self.calcular_memoria_hora_mundial()
        self.procesos_activos["Hora Mundial"] = {
            "frame": self.hora_frame,
            "memoria": memoria_usada,
            "hilos": self.threads
        }
        self.desktop_app.actualizar_procesos_activos()

    def update_times(self):
        while not self.stopped.is_set():
            for city in self.cities:
                if self.stopped.is_set():
                    return  # Salir del ciclo si se detiene
                thread = Thread(target=self.fetch_data, args=(city,), daemon=True)
                self.threads.append(thread)
                thread.start()
            time.sleep(60)  # Esperar un minuto antes de actualizar nuevamente

    def fetch_data(self, city):
        try:
            response = requests.get(f"http://worldtimeapi.org/api/timezone/{city}", timeout=10)
            if self.stopped.is_set():
                return  # Detener si la señal se activa
            if response.status_code == 200:
                current_time = response.json()['datetime']
                self.labels[city].config(text=f"{city.split('/')[1]}: {current_time}")
            else:
                self.labels[city].config(text=f"{city.split('/')[1]}: Error")
        except requests.exceptions.RequestException as e:
            if not self.stopped.is_set():
                print(f"Error obteniendo datos para {city}: {e}")
                self.labels[city].config(text=f"{city.split('/')[1]}: Error")

    def cerrar_hora_mundial(self):
        # Detener todos los hilos
        self.stopped.set()
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1)  # Forzar cierre después de un tiempo
        self.threads.clear()  # Limpiar la lista de hilos

        # Limpiar y destruir el frame
        for widget in self.hora_frame.winfo_children():
            widget.destroy()
        self.hora_frame.pack_forget()

        # Eliminar el proceso de la lista activa
        if "Hora Mundial" in self.procesos_activos:
            del self.procesos_activos["Hora Mundial"]
        self.desktop_app.actualizar_procesos_activos()

    def calcular_memoria_hora_mundial(self):
        memoria_base = 30
        num_items = len(self.hora_frame.winfo_children()) * 1
        return memoria_base + num_items
    







class TextApp:
    instance_counter = 0  # Contador para asignar identificadores únicos a las instancias

    def __init__(self, desktop_app, file_path=None):
        self.desktop_app = desktop_app
        self.text_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=500, height=400)
        self.text_frame.pack_propagate(False)
        self.text_frame.pack(padx=10, pady=10)

        self.file_path = file_path

        # Asignar un identificador único a la instancia
        TextApp.instance_counter += 1
        self.instance_id = f"Editor de Texto {TextApp.instance_counter}"

        self.setup_ui()
        if file_path:
            self.load_file(file_path)

        # Registrar el proceso en el Administrador de Tareas
        memoria_usada = self.calcular_memoria_editor()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.text_frame,
            "memoria": memoria_usada,
            "app": self,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado y botón cerrar
        top_frame = tk.Frame(self.text_frame, bg="lightgray")
        top_frame.pack(fill="x")
        close_button = tk.Button(
            top_frame, text="X", command=self.close_text_editor,
            bg="red", fg="white", font=("Arial", 12, "bold")
        )
        close_button.pack(side="right")

        # Frame para título y botón guardar
        title_frame = tk.Frame(self.text_frame, bg="lightgray")
        title_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(title_frame, text="Título del archivo:", bg="lightgray", font=("Arial", 12)).pack(side="left", padx=5)

        self.file_name_entry = tk.Entry(title_frame, font=("Arial", 12), width=30)
        self.file_name_entry.pack(side="left", padx=5, fill="x", expand=True)

        save_button = tk.Button(
            title_frame,
            text="Guardar",
            command=self.save_file,
            bg="blue", fg="white", font=("Arial", 12)
        )
        save_button.pack(side="left", padx=5)

        # Área de texto
        self.text_area = tk.Text(self.text_frame, wrap="word", font=("Arial", 12))
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)

    def load_file(self, path):
        """Carga el contenido de un archivo de texto existente."""
        try:
            with open(path, 'r', encoding="utf-8") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                file_name = os.path.basename(path)
                self.file_name_entry.insert(0, file_name)
        except Exception as e:
            self.show_message(f"Error al cargar archivo: {e}", "red")

    def save_file(self):
        """Guarda el archivo de texto en la carpeta 'Documentos' del usuario."""
        file_name = self.file_name_entry.get().strip()
        if not file_name:
            self.show_message("Por favor, ingresa un nombre para el archivo.", "red")
            return

        file_name += ".txt"
        # Definir ruta de guardado
        user_directory = self.desktop_app.auth.cargar_directorio_usuario()
        documents_directory = os.path.join(user_directory, "Documentos")
        if not os.path.exists(documents_directory):
            os.makedirs(documents_directory)

        file_path = os.path.join(documents_directory, file_name)

        try:
            with open(file_path, 'w', encoding="utf-8") as file:
                content = self.text_area.get(1.0, tk.END).strip()
                file.write(content)
            self.show_message(f"Guardado en: {file_path}", "green")
        except Exception as e:
            self.show_message(f"Error al guardar archivo: {e}", "red")

    def calcular_memoria_editor(self):
        """Calcula la memoria usada por el editor."""
        memoria_base = 30
        elementos_extra = len(self.text_frame.winfo_children())
        return memoria_base + elementos_extra

    def close_text_editor(self):
        """Cierra el editor de texto desde cualquier parte."""
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.text_frame.pack_forget()
        self.desktop_app.actualizar_procesos_activos()

    def show_message(self, message, color):
        """Muestra mensajes informativos en la ventana de texto."""
        msg_label = tk.Label(self.text_frame, text=message, fg=color, bg="lightgray", font=("Arial", 10))
        msg_label.pack(pady=5, anchor="w")










class MusicPlayerApp:
    instance_counter = 0  # Contador para asignar identificadores únicos a las instancias

    def __init__(self, desktop_app, path=None):
        self.desktop_app = desktop_app
        self.music_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=300, height=200)
        self.music_frame.pack_propagate(False)
        self.music_frame.pack(padx=10, pady=10)

        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.audio_length = 0
        self.slider_locked = False
        self.playlist = []
        self.current_index = 0

        # Identificador único para esta instancia
        MusicPlayerApp.instance_counter += 1
        self.instance_id = f"Reproductor {MusicPlayerApp.instance_counter}"

        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)

        self.setup_ui()

        # Cargar canciones desde el path proporcionado
        if path:
            self.load_from_path(path)
        else:
            self.load_default_directory()

        # Registrar el proceso en el Administrador de Tareas
        memoria_usada = self.calcular_memoria_reproductor()
        hilo = threading.Thread(target=self.hilo_reproductor, daemon=True)
        hilo.start()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.music_frame,
            "memoria": memoria_usada,
            "hilo": hilo,
            "app": self,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado y botón cerrar
        top_frame = tk.Frame(self.music_frame, bg="lightgray")
        top_frame.pack(fill="x")
        close_button = tk.Button(
            top_frame, text="X", command=self.close_music_player, bg="red", fg="white"
        )
        close_button.pack(side="right")

        # Visor de información
        self.song_label = tk.Label(
            self.music_frame, text="Ningún archivo cargado", bg="lightgray", anchor="center", wraplength=250
        )
        self.song_label.pack(pady=5)

        # Botones de control
        control_frame = tk.Frame(self.music_frame, bg="lightgray")
        control_frame.pack(pady=5)
        self.back_button = tk.Button(control_frame, text="⏪", command=self.play_prev, width=4)
        self.back_button.grid(row=0, column=0, padx=5)
        self.play_button = tk.Button(control_frame, text="▶️", command=self.play_pause_music, width=4)
        self.play_button.grid(row=0, column=1, padx=5)
        self.stop_button = tk.Button(control_frame, text="⏹", command=self.stop_music, width=4)
        self.stop_button.grid(row=0, column=2, padx=5)
        self.forward_button = tk.Button(control_frame, text="⏩", command=self.play_next, width=4)
        self.forward_button.grid(row=0, column=3, padx=5)

        # Sliders de progreso y volumen
        sliders_frame = tk.Frame(self.music_frame, bg="lightgray")
        sliders_frame.pack(fill="x", padx=10, pady=5)

        # Slider de progreso
        self.progress = ttk.Scale(sliders_frame, from_=0, to=100, orient="horizontal", command=self.on_slider_move)
        self.progress.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress.bind("<ButtonRelease-1>", self.on_slider_release)
        self.progress.grid(row=0, column=0, sticky="we", padx=5)
        sliders_frame.columnconfigure(0, weight=3)

        # Slider de volumen
        self.volume = ttk.Scale(sliders_frame, from_=0, to=1, orient="horizontal", command=self.set_volume, length=80)
        self.volume.set(0.5)
        self.volume.grid(row=0, column=1, sticky="e", padx=5)

        # Tiempo de reproducción
        self.time_label = tk.Label(self.music_frame, text="00:00 / 00:00", bg="lightgray")
        self.time_label.pack(pady=5)

    def load_default_directory(self):
        """Carga canciones desde el directorio por defecto del usuario."""
        user_directory = self.desktop_app.auth.cargar_directorio_usuario()
        if not user_directory:
            self.song_label.config(text="Error: No se encontró el directorio del usuario.")
            return

        music_directory = os.path.join(user_directory, "Música")
        if not os.path.exists(music_directory):
            self.song_label.config(text="Error: No se encontró la carpeta 'Música'.")
            return

        self.load_from_path(music_directory)

    def load_from_path(self, path):
        """Carga canciones desde un directorio o un archivo."""
        if os.path.isfile(path):
            directory = os.path.dirname(path)
            self.playlist = [
                os.path.join(directory, file)
                for file in os.listdir(directory)
                if file.lower().endswith((".mp3", ".wav", ".ogg"))
            ]
            self.current_index = self.playlist.index(path)
        elif os.path.isdir(path):
            self.playlist = [
                os.path.join(path, file)
                for file in os.listdir(path)
                if file.lower().endswith((".mp3", ".wav", ".ogg"))
            ]
            self.current_index = 0
        else:
            self.song_label.config(text="Error: No se puede cargar el archivo o directorio.")
            return

        if not self.playlist:
            self.song_label.config(text="No se encontraron archivos de audio en la carpeta.")
            return

        self.load_file(self.playlist[self.current_index])

    def load_file(self, file_path):
        """Carga un archivo de música."""
        self.current_file = file_path
        pygame.mixer.music.load(file_path)
        self.audio_length = int(pygame.mixer.Sound(file_path).get_length())
        self.song_label.config(text=f"Cargado: {os.path.basename(file_path)}")
        self.progress.config(to=self.audio_length)
        self.time_label.config(
            text=f"00:00 / {time.strftime('%M:%S', time.gmtime(self.audio_length))}"
        )
        self.stop_music()

    def play_pause_music(self):
        if not self.current_file:
            return
        if not self.is_playing:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.play_button.config(text="⏸")
            threading.Thread(target=self.update_progress, daemon=True).start()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_button.config(text="⏸")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_button.config(text="▶️")

    def play_next(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.load_file(self.playlist[self.current_index])
        self.play_pause_music()

    def play_prev(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.load_file(self.playlist[self.current_index])
        self.play_pause_music()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.config(text="▶️")
        self.progress.set(0)
        self.time_label.config(text="00:00 / 00:00")

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))

    def on_slider_move(self, value):
        if self.slider_locked:
            current_time = int(float(value))
            self.time_label.config(
                text=f"{time.strftime('%M:%S', time.gmtime(current_time))} / {time.strftime('%M:%S', time.gmtime(self.audio_length))}"
            )

    def on_slider_press(self, event):
        self.slider_locked = True

    def on_slider_release(self, event):
        self.slider_locked = False
        if self.current_file:
            new_position = int(self.progress.get())
            pygame.mixer.music.set_pos(new_position)

    def update_progress(self):
        while self.is_playing:
            if not self.is_paused and not self.slider_locked:
                current_time = pygame.mixer.music.get_pos() // 1000
                if current_time >= 0:
                    self.progress.set(current_time)
                    self.time_label.config(
                        text=f"{time.strftime('%M:%S', time.gmtime(current_time))} / {time.strftime('%M:%S', time.gmtime(self.audio_length))}"
                    )
            time.sleep(1)

    def calcular_memoria_reproductor(self):
        """Calcula la memoria usada por el reproductor."""
        memoria_base = 50
        elementos_extra = len(self.music_frame.winfo_children())
        return memoria_base + elementos_extra

    def hilo_reproductor(self):
        while self.is_playing:
            time.sleep(1)

    def close_music_player(self):
        self.stop_music()
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.music_frame.pack_forget()
        self.desktop_app.actualizar_procesos_activos()














class ImageViewerApp:
    instance_counter = 0

    def __init__(self, desktop_app, path=None):
        self.desktop_app = desktop_app
        self.instance_id = f"Visualizador {ImageViewerApp.instance_counter}"
        ImageViewerApp.instance_counter += 1

        # Crear el marco principal
        self.image_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=600, height=400)
        self.image_frame.pack_propagate(False)
        self.image_frame.pack(padx=10, pady=10)

        self.images = []  # Lista de imágenes cargadas
        self.image_paths = []  # Rutas de las imágenes cargadas
        self.current_index = 0  # Índice de la imagen actual
        self.zoom_level = 1.0  # Nivel de zoom

        self.setup_ui()

        if path:
            self.load_from_path(path)
        else:
            self.load_images_from_user_directory()

        # Registrar la aplicación en el Administrador de Tareas
        memoria_usada = self.calcular_memoria()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.image_frame,
            "close_method": self.close_image_viewer,
            "memoria": memoria_usada,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado y botón cerrar
        top_frame = tk.Frame(self.image_frame, bg="lightgray")
        top_frame.pack(fill="x")

        close_button = tk.Button(top_frame, text="X", command=self.close_image_viewer, bg="red", fg="white")
        close_button.pack(side="right")

        # Canvas para mostrar la imagen o mensajes
        self.canvas = tk.Canvas(self.image_frame, bg="white", width=600, height=300)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Controles de navegación
        controls_frame = tk.Frame(self.image_frame, bg="lightgray")
        controls_frame.pack(fill="x", padx=10, pady=5)

        self.prev_button = tk.Button(controls_frame, text="⟵", command=self.show_prev_image)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.zoom_slider = ttk.Scale(
            controls_frame, from_=0.5, to=3.0, orient="horizontal", value=self.zoom_level, command=self.update_zoom
        )
        self.zoom_slider.grid(row=0, column=1, sticky="we", padx=10)
        controls_frame.columnconfigure(1, weight=1)

        self.next_button = tk.Button(controls_frame, text="⟶", command=self.show_next_image)
        self.next_button.grid(row=0, column=2, padx=5)

    def load_from_path(self, path):
        """Carga una imagen específica o todas las imágenes de un directorio."""
        if os.path.isfile(path):
            directory = os.path.dirname(path)
            self.image_paths = [
                os.path.join(directory, file)
                for file in os.listdir(directory)
                if file.lower().endswith((".jpg", ".png", ".jpeg", ".bmp"))
            ]
            self.current_index = self.image_paths.index(path)
        elif os.path.isdir(path):
            self.image_paths = [
                os.path.join(path, file)
                for file in os.listdir(path)
                if file.lower().endswith((".jpg", ".png", ".jpeg", ".bmp"))
            ]
            self.current_index = 0

        if not self.image_paths:
            self.show_message("No se encontraron imágenes.")
            return

        self.images = [Image.open(image_path) for image_path in self.image_paths]
        self.zoom_level = 1.0
        self.zoom_slider.set(self.zoom_level)
        self.display_image()

    def load_images_from_user_directory(self):
        """Carga imágenes de la carpeta 'Imágenes' del usuario."""
        user_directory = self.desktop_app.auth.cargar_directorio_usuario()
        if not user_directory:
            self.show_message("Directorio de usuario no encontrado.")
            return

        images_directory = os.path.join(user_directory, "Imágenes")
        self.load_from_path(images_directory)

    def display_image(self):
        """Muestra la imagen actual con el zoom aplicado."""
        if not self.images:
            return

        image = self.images[self.current_index]
        zoomed_image = image.resize(
            (int(image.width * self.zoom_level), int(image.height * self.zoom_level)), Image.Resampling.LANCZOS
        )
        self.tk_image = ImageTk.PhotoImage(zoomed_image)

        self.canvas.delete("all")
        self.canvas.create_image(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            image=self.tk_image,
            anchor="center",
        )

    def show_prev_image(self):
        """Muestra la imagen anterior."""
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.zoom_level = 1.0
            self.zoom_slider.set(self.zoom_level)
            self.display_image()

    def show_next_image(self):
        """Muestra la siguiente imagen."""
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)
            self.zoom_level = 1.0
            self.zoom_slider.set(self.zoom_level)
            self.display_image()

    def update_zoom(self, value):
        """Actualiza el zoom de la imagen."""
        self.zoom_level = float(value)
        self.display_image()

    def show_message(self, message):
        """Muestra un mensaje en el canvas."""
        self.canvas.delete("all")
        self.canvas.create_text(
            300, 150, text=message, fill="red", font=("Arial", 16)
        )

    def calcular_memoria(self):
        """Calcula la memoria utilizada por el visor de imágenes."""
        memoria_base = 50
        return memoria_base + len(self.image_paths) * 5

    def close_image_viewer(self):
        """Cierra el visor de imágenes."""
        self.image_frame.pack_forget()
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.desktop_app.actualizar_procesos_activos()









class SnakeApp:
    instance_counter = 0  # Contador para instancias únicas

    def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        self.instance_id = f"Snake {SnakeApp.instance_counter}"
        SnakeApp.instance_counter += 1

        self.snake_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=800, height=600)
        self.snake_frame.pack_propagate(False)
        self.snake_frame.pack(padx=10, pady=10)

        self.running = False
        self.paused = False
        self.score = 0
        self.snake = [(5, 5)]  # Lista de posiciones del cuerpo de la serpiente
        self.food = (0, 0)  # Posición de la comida
        self.direction = "Right"  # Dirección inicial
        self.grid_size = 20  # Tamaño del grid
        self.cell_size = 20  # Tamaño de cada celda

        self.setup_ui()
        self.reset_game()

        # Registrar en el Administrador de Tareas
        memoria_usada = self.calcular_memoria()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.snake_frame,
            "close_method": self.close_snake_game,
            "memoria": memoria_usada,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado y botones
        top_frame = tk.Frame(self.snake_frame, bg="lightgray")
        top_frame.pack(fill="x")

        # Botones en el encabezado
        new_game_button = tk.Button(top_frame, text="Nueva Partida", command=self.reset_game, bg="blue", fg="white", width=12, height=1)
        new_game_button.pack(side="left", padx=5)

        pause_button = tk.Button(top_frame, text="Pausa", command=self.toggle_pause, bg="orange", fg="white", width=8, height=1)
        pause_button.pack(side="left", padx=5)

        close_button = tk.Button(top_frame, text="X", command=self.close_snake_game, bg="red", fg="white", width=3, height=1)
        close_button.pack(side="right")

        # Mensaje de estado
        self.message_label = tk.Label(self.snake_frame, text="", bg="lightgray", font=("Arial", 12), fg="red")
        self.message_label.pack(pady=5)

        # Barra de puntuación
        self.score_label = tk.Label(self.snake_frame, text=f"Puntuación: {self.score}", bg="lightgray", font=("Arial", 12))
        self.score_label.pack(pady=5)

        # Canvas para el juego
        self.canvas = tk.Canvas(
            self.snake_frame,
            bg="black",
            width=self.grid_size * self.cell_size,
            height=self.grid_size * self.cell_size,
        )
        self.canvas.pack(padx=10, pady=10)

        # Enlazar las teclas de dirección
        self.desktop_app.window.bind("<Up>", lambda event: self.change_direction("Up"))
        self.desktop_app.window.bind("<Down>", lambda event: self.change_direction("Down"))
        self.desktop_app.window.bind("<Left>", lambda event: self.change_direction("Left"))
        self.desktop_app.window.bind("<Right>", lambda event: self.change_direction("Right"))

    def reset_game(self):
        """Reinicia el juego pero no lo inicia automáticamente."""
        self.running = False
        self.paused = False
        self.score = 0
        self.snake = [(5, 5)]
        self.direction = "Right"
        self.message_label.config(text="Presiona 'Pausa' para empezar el juego")
        self.place_food()
        self.update_score()
        self.draw_game()

    def start_game(self):
        """Inicia el juego."""
        if not self.running:
            self.running = True
            self.message_label.config(text="")
            self.run_game()

    def toggle_pause(self):
        """Pausa o reanuda el juego."""
        if self.running:
            self.paused = not self.paused
            if self.paused:
                self.message_label.config(text="Juego Pausado")
            else:
                self.message_label.config(text="")
        else:
            self.start_game()

    def update_score(self):
        """Actualiza la puntuación en la interfaz."""
        self.score_label.config(text=f"Puntuación: {self.score}")

    def place_food(self):
        """Coloca la comida en una posición aleatoria que no choque con la serpiente."""
        while True:
            self.food = (random.randint(2, self.grid_size - 2), random.randint(2, self.grid_size - 2))
            if self.food not in self.snake:
                break

    def change_direction(self, new_direction):
        """Cambia la dirección de la serpiente, evitando giros de 180°."""
        if (new_direction == "Up" and self.direction != "Down") or \
           (new_direction == "Down" and self.direction != "Up") or \
           (new_direction == "Left" and self.direction != "Right") or \
           (new_direction == "Right" and self.direction != "Left"):
            self.direction = new_direction

    def run_game(self):
        """Lógica principal del juego."""
        if self.running and not self.paused:
            self.move_snake()
            self.check_collisions()
            self.draw_game()
        if self.running:
            self.snake_frame.after(100, self.run_game)  # Velocidad del juego

    def move_snake(self):
        """Mueve la serpiente en la dirección actual."""
        head_x, head_y = self.snake[-1]
        if self.direction == "Up":
            head_y -= 1
        elif self.direction == "Down":
            head_y += 1
        elif self.direction == "Left":
            head_x -= 1
        elif self.direction == "Right":
            head_x += 1
        new_head = (head_x, head_y)
        self.snake.append(new_head)

        if new_head == self.food:
            self.score += 1
            self.place_food()
            self.update_score()
        else:
            self.snake.pop(0)

    def check_collisions(self):
        """Verifica si la serpiente choca con las paredes o consigo misma."""
        head_x, head_y = self.snake[-1]
        if head_x < 0 or head_x >= self.grid_size or head_y < 0 or head_y >= self.grid_size:
            self.game_over()
        if len(self.snake) != len(set(self.snake)):  # Verifica si hay duplicados (auto-colisión)
            self.game_over()

    def draw_game(self):
        """Dibuja la serpiente y la comida en el canvas."""
        self.canvas.delete("all")

        # Dibuja la serpiente
        for segment in self.snake:
            x1 = segment[0] * self.cell_size
            y1 = segment[1] * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="")

        # Dibuja la comida
        food_x1 = self.food[0] * self.cell_size
        food_y1 = self.food[1] * self.cell_size
        food_x2 = food_x1 + self.cell_size
        food_y2 = food_y1 + self.cell_size
        self.canvas.create_oval(food_x1, food_y1, food_x2, food_y2, fill="red", outline="")

    def game_over(self):
        """Finaliza el juego."""
        self.running = False
        self.paused = False
        self.message_label.config(text=f"Game Over - Puntuación final: {self.score}")

    def calcular_memoria(self):
        """Calcula la memoria utilizada por el juego."""
        memoria_base = 30
        return memoria_base + len(self.snake) * 5

    def close_snake_game(self):
        """Cierra la ventana del juego."""
        self.running = False
        self.snake_frame.pack_forget()
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.desktop_app.actualizar_procesos_activos()








class BrowserApp:
    instance_counter = 0  # Contador de instancias únicas

    def __init__(self, desktop_app, initial_url="https://www.google.com"):
        self.desktop_app = desktop_app
        self.instance_id = f"Navegador {BrowserApp.instance_counter}"
        BrowserApp.instance_counter += 1

        self.browser_frame = tk.Frame(self.desktop_app.window, bg="white", width=800, height=600)
        self.browser_frame.pack_propagate(False)
        self.browser_frame.pack(padx=10, pady=10)

        self.initial_url = initial_url
        self.setup_ui()
        self.load_url(self.initial_url)

        # Registrar en el Administrador de Tareas
        memoria_usada = self.calcular_memoria()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.browser_frame,
            "close_method": self.close_browser,
            "memoria": memoria_usada,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado y botón cerrar
        top_frame = tk.Frame(self.browser_frame, bg="lightgray")
        top_frame.pack(fill="x")

        close_button = tk.Button(
            top_frame, text="X", command=self.close_browser, bg="red", fg="white", font=("Arial", 12, "bold")
        )
        close_button.pack(side="right", padx=5)

        self.address_bar = tk.Entry(top_frame, font=("Arial", 12))
        self.address_bar.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        go_button = tk.Button(top_frame, text="Ir", command=self.go_to_url, bg="blue", fg="white", font=("Arial", 10))
        go_button.pack(side="right", padx=5)

        # Marco HTML para mostrar contenido
        self.html_view = HtmlFrame(self.browser_frame)
        self.html_view.pack(fill="both", expand=True)

    def load_url(self, url):
        """Carga una URL en el navegador."""
        try:
            self.html_view.load_website(url)
        except Exception as e:
            print(f"Error al cargar la URL: {e}")

    def go_to_url(self):
        """Obtiene la URL del cuadro de texto y la carga."""
        url = self.address_bar.get().strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        self.load_url(url)

    def calcular_memoria(self):
        """Calcula la memoria utilizada por el navegador."""
        memoria_base = 50
        return memoria_base

    def close_browser(self):
        """Cierra el navegador."""
        self.browser_frame.pack_forget()
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.desktop_app.actualizar_procesos_activos()





class VideoPlayerApp:
    instance_counter = 0

    def __init__(self, desktop_app, video_path=None):
        self.desktop_app = desktop_app
        # Aumentamos las dimensiones de la ventana
        self.video_frame = tk.Frame(self.desktop_app.window, bg="lightgray", width=900, height=600)
        self.video_frame.pack_propagate(False)
        self.video_frame.pack(padx=10, pady=10)

        self.video_path = None
        self.video_capture = None
        self.playing = False
        self.paused = False
        self.current_time = 0
        self.total_time = 0
        self.thread = None
        self.stop_thread = threading.Event()

        self.instance_id = f"VideoPlayer_{VideoPlayerApp.instance_counter}"
        VideoPlayerApp.instance_counter += 1

        self.setup_ui()

        if video_path:
            self.load_video(video_path)

        # Registro en el administrador de tareas
        memoria_usada = self.calcular_memoria()
        self.desktop_app.procesos_activos[self.instance_id] = {
            "frame": self.video_frame,
            "memoria": memoria_usada,
            "hilo": self.thread,
        }
        self.desktop_app.actualizar_procesos_activos()

    def setup_ui(self):
        # Encabezado con botón de cerrar
        top_frame = tk.Frame(self.video_frame, bg="lightgray")
        top_frame.pack(fill="x")
        close_button = tk.Button(
            top_frame, text="X", command=self.close_video_player, bg="red", fg="white", font=("Arial", 12, "bold")
        )
        close_button.pack(side="right")

        # Canvas para mostrar el video
        # Aumentamos el tamaño del lienzo
        self.canvas = tk.Canvas(self.video_frame, bg="black", width=850, height=450)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Controles de reproducción
        controls_frame = tk.Frame(self.video_frame, bg="lightgray")
        controls_frame.pack(fill="x", padx=10, pady=5)

        self.play_button = tk.Button(controls_frame, text="▶️", command=self.toggle_play_pause, width=5)
        self.play_button.grid(row=0, column=0, padx=5)

        open_button = tk.Button(controls_frame, text="📂", command=self.open_file, width=5)
        open_button.grid(row=0, column=2, padx=5)

        # Escala y controles más amplios para adaptarse al nuevo tamaño
        self.slider = ttk.Scale(
            controls_frame, from_=0, to=100, orient="horizontal",
        )
        self.slider.grid(row=0, column=3, sticky="we", padx=10)
        controls_frame.columnconfigure(3, weight=1)

        self.time_label = tk.Label(controls_frame, text="00:00 / 00:00", bg="lightgray")
        self.time_label.grid(row=0, column=4, padx=5)

    def open_file(self):
        """Abre un archivo de video desde el sistema de archivos."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de video", "*.mp4 *.avi *.mkv *.mov")]
        )
        if file_path:
            self.load_video(file_path)

    def load_video(self, video_path):
        """Carga un video desde una ruta proporcionada."""
        self.stop_video()  # Detén cualquier video en reproducción

        try:
            # Crear un nuevo objeto de captura
            video_capture = cv2.VideoCapture(video_path)

            # Validar si el video se abrió correctamente
            if not video_capture.isOpened():
                raise ValueError("No se pudo abrir el video. El archivo puede estar corrupto o no compatible.")

            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video_capture.get(cv2.CAP_PROP_FPS)

            if total_frames == 0 or fps == 0:
                raise ValueError("El archivo de video no contiene datos reproducibles.")

            # Liberar recursos del video anterior
            if self.video_capture:
                self.video_capture.release()

            # Asignar el nuevo video
            self.video_capture = video_capture
            self.video_path = video_path
            self.total_time = total_frames / fps
            self.slider.config(to=self.total_time)

            # Actualizar la etiqueta de tiempo
            self.update_time_label()
            self.play_video()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el video: {e}")
            if self.video_capture:
                self.video_capture.release()
            self.video_capture = None


    def play_video(self):
        """Inicia la reproducción del video."""
        if not self.video_capture or self.playing:
            return

        self.playing = True
        self.paused = False
        self.stop_thread.clear()
        self.thread = threading.Thread(target=self._play_video_thread, daemon=True)
        self.thread.start()

    def _play_video_thread(self):
        """Hilo de reproducción de video."""
        try:
            while self.playing and not self.stop_thread.is_set():
                if self.paused:
                    time.sleep(0.1)
                    continue

                ret, frame = self.video_capture.read()
                if not ret:
                    break

                self.current_time += 1 / self.video_capture.get(cv2.CAP_PROP_FPS)
                self.slider.set(self.current_time)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                tk_image = ImageTk.PhotoImage(image)

                self.canvas.create_image(0, 0, anchor="nw", image=tk_image)
                self.canvas.image = tk_image
                self.canvas.update()

                time.sleep(1 / self.video_capture.get(cv2.CAP_PROP_FPS))
        except Exception as e:
            print(f"Error durante la reproducción del video: {e}")

        self.stop_video()

    def toggle_play_pause(self):
        """Pausa o reanuda la reproducción del video."""
        if self.playing:
            self.paused = not self.paused
            self.play_button.config(text="▶️" if self.paused else "⏸")

    def stop_video(self):
        """Detiene la reproducción del video."""
        self.playing = False
        self.paused = False
        self.stop_thread.set()
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None

        self.current_time = 0
        self.slider.set(self.current_time)
        self.canvas.delete("all")

    def on_slider_move(self, value):
        """Actualiza la posición del video cuando se mueve el slider."""
        try:
            new_time = float(value)
            self.current_time = new_time
            self.update_time_label()
            if self.video_capture:
                self.video_capture.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)
        except Exception:
            pass

    def update_time_label(self):
        """Actualiza el texto del temporizador."""
        current_time_str = time.strftime("%M:%S", time.gmtime(self.current_time))
        total_time_str = time.strftime("%M:%S", time.gmtime(self.total_time))
        self.time_label.config(text=f"{current_time_str} / {total_time_str}")

    def close_video_player(self):
        """Cierra el reproductor de video y elimina la instancia."""
        self.stop_video()
        self.video_frame.pack_forget()
        if self.instance_id in self.desktop_app.procesos_activos:
            del self.desktop_app.procesos_activos[self.instance_id]
        self.desktop_app.actualizar_procesos_activos()

    def calcular_memoria(self):
        """Calcula la memoria utilizada por el reproductor de video."""
        memoria_base = 50
        if self.video_capture:
            memoria_base += int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) * 0.01
        return memoria_base


if __name__ == "__main__":

    DesktopApp()