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


    def registrar_usuario(self, username, password):
        if username in self.usuarios:
            return False
        self.usuarios[username] = {"password": self.cifrar_contraseña(password)}
        self.guardar_usuarios()


        #Crea una carpeta en el directorio usuarios con el nombre del usuario
        user_directory = f"./usuarios/{username}"
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)


        #ademas crea las carpetas de documentos, descargas, musica, videos e imagenes
        carpetas = ["Documentos", "Descargas", "Música", "Videos", "Imágenes"]
        for carpeta in carpetas:
            carpeta_path = os.path.join(user_directory, carpeta)
            if not os.path.exists(carpeta_path):
                os.makedirs(carpeta_path)




        return True


    def cargar_directorio_usuario(self):
        if self.usuario_actual:
            user_directory = f"./usuarios/{self.usuario_actual}"
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
            return user_directory
        return None


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


        self.create_welcome_screen()
       
        self.message_label = tk.Label(self.window, text="", font=("Arial", 12), bg="white", fg="green")
        self.message_label.pack(pady=10)








        # Iniciar el reloj
        self.update_clock()


   




        self.window.mainloop()
       # Crear etiqueta para mostrar mensajes






    def create_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.window, bg="white")
        self.welcome_frame.pack(fill="both", expand=True)
        welcome_label = tk.Label(self.welcome_frame, text="Bienvenido", font=("Arial", 24), bg="white")
        welcome_label.pack(pady=50)

        # se carga el logo por medio del os de pyhton
        logo_path = os.path.join(os.getcwd(), "images", "s1.png")
        if os.path.exists(logo_path):
            logo = tk.PhotoImage(file=logo_path)
            logo_label = tk.Label(self.welcome_frame, image=logo)
            logo_label.image = logo  # Keep a reference to avoid garbage collection
            logo_label.pack(pady=50)
        else:
            logo_label = tk.Label(self.welcome_frame, text="Logo no encontrado", font=("Arial", 14), bg="white", fg="red")
            logo_label.pack(pady=50)


        login_button = tk.Button(self.welcome_frame, text="Iniciar Sesión", font=("Arial", 14), command=self.mostrar_inicio_sesion)
        login_button.pack(pady=10)


        register_button = tk.Button(self.welcome_frame, text="Registrar", font=("Arial", 14), command=self.mostrar_registro)
        register_button.pack(pady=10)


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












    def mostrar_registro(self):
        # Limpiar el marco de autenticación antes de mostrar el formulario de registro
        self._limpiar_frame(self.auth_frame)


        tk.Label(self.auth_frame, text="Nuevo Usuario").pack(pady=5)
        registro_username = tk.Entry(self.auth_frame)
        registro_username.pack(pady=5)


        tk.Label(self.auth_frame, text="Contraseña").pack(pady=5)
        registro_password = tk.Entry(self.auth_frame, show="*")
        registro_password.pack(pady=5)


        def intentar_registrar_usuario():
            if not self.message_label.winfo_exists():
                return  # Evitar errores si la ventana ha sido destruida


            username = registro_username.get()
            password = registro_password.get()
            if self.auth.registrar_usuario(username, password):
                self.message_label.config(text="Usuario registrado con éxito.", fg="green")
                self.mostrar_inicio_sesion()  # Redirigir al inicio de sesión después de registrar
                self.window.after(4000, self.limpiar_mensaje)  # Limpiar el mensaje después de 4 segundos
            else:
                self.message_label.config(text="El usuario ya existe.", fg="red")
                self.window.after(4000, self.limpiar_mensaje)  # Limpiar el mensaje después de 4 segundos


        tk.Button(self.auth_frame, text="Registrar", command=intentar_registrar_usuario).pack(pady=10)




    def create_taskbar(self):
        self.taskbar = tk.Frame(self.window, bg="gray", height=40)
        self.start_button = tk.Button(self.taskbar, text="Inicio", command=self.toggle_menu, bg="lightgray")
        self.start_button.pack(side="left", padx=5)
        self.clock_label = tk.Label(self.taskbar, font=("Arial", 12), bg="gray", fg="white")
        self.clock_label.pack(side="right", padx=10)


    def create_menu(self):
        self.menu_frame = tk.Frame(self.window, bg="lightgray", width=200, height=300)
        programs = ["Calculadora", "Explorador","Administrador de Tareas","Horarios","Apagar"]
        for program in programs:
            if program == "Apagar":
                button = tk.Button(self.menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=self.apagar)
            elif program == "Administrador de Tareas":
                button = tk.Button(self.menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=self.toggle_task_manager)
            else:
                button = tk.Button(self.menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=lambda p=program: self.abrir_aplicacion(p))
            button.pack(pady=2)


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
            ExplorerApp(self)
        elif nombre_aplicacion == "Horarios":
            WorldTimeApp(self)
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
    def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        self.cola_calculadora = desktop_app.cola_calculadora
        self.calculator_frame = desktop_app.calculator_frame  # Usar el marco existente
        self.procesos_activos = desktop_app.procesos_activos
        self.mostrar_calculadora()

    def mostrar_calculadora(self):
        # Limpiar la calculadora antes de mostrarla
        for widget in self.calculator_frame.winfo_children():
            widget.destroy()

        self.calculator_frame.pack(side="right", fill="both", padx=10, pady=10)

        # Crear el frame superior con el botón de cerrar
        top_frame = tk.Frame(self.calculator_frame, bg="lightgray")
        top_frame.grid(row=0, column=0, columnspan=8, sticky="we")
        close_button = tk.Button(top_frame, text="X", command=self.cerrar_calculadora, bg="red", fg="white", font=("Arial", 12, "bold"))
        close_button.pack(side="right")

        # Entrada de texto de la calculadora
        self.entry = tk.Entry(self.calculator_frame, width=35, font=("Arial", 18), borderwidth=2, relief="solid", justify='right')
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

        # Calcular y actualizar la memoria de la calculadora
        memoria_usada = self.calcular_memoria_calculadora()
        hilo = threading.Thread(target=self.hilo_calculadora, args=(self.cola_calculadora,), daemon=True)
        hilo.start()
        self.procesos_activos["Calculadora"] = {"frame": self.calculator_frame, "memoria": memoria_usada, "hilo": hilo, "cola": self.cola_calculadora}
        self.desktop_app.actualizar_procesos_activos()

    def process_button(self, value):
        if value == '=':
            self.calcular_resultado()
        elif value == 'AC':
            self.entry.delete(0, tk.END)
        elif value == 'C':
            self.entry.delete(len(self.entry.get())-1, tk.END)
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
        if "Calculadora" in self.procesos_activos:
            del self.procesos_activos["Calculadora"]
        self.desktop_app.actualizar_procesos_activos()

    def calcular_memoria_calculadora(self):
        memoria_base = 20
        memoria_adicional = len(self.calculator_frame.winfo_children()) * 2
        return memoria_base + memoria_adicional

    def hilo_calculadora(self, cola):
        while True:
            mensaje = cola.get()
            if mensaje == "cerrar":
                break


class ExplorerApp:
    def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        self.cola_explorador = desktop_app.cola_explorador
        self.explorer_frame = desktop_app.explorer_frame
        self.procesos_activos = desktop_app.procesos_activos




        self.mostrar_explorador()




    def mostrar_explorador(self):
        for widget in self.explorer_frame.winfo_children():
            widget.destroy()
        self.explorer_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)




        top_frame = tk.Frame(self.explorer_frame, bg="lightgray")
        top_frame.pack(fill="x")
        close_button = tk.Button(top_frame, text="X", command=self.cerrar_explorador, bg="red", fg="white", font=("Arial", 12, "bold"))
        close_button.pack(side="right")




        initial_path = os.getcwd()
        path_label = tk.Label(self.explorer_frame, text=initial_path, anchor="w")
        path_label.pack(fill="x", padx=10, pady=5)




        tree = ttk.Treeview(self.explorer_frame, columns=("fullpath",), show="tree")
        tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.update_directory_tree(tree, initial_path)




        back_button = tk.Button(self.explorer_frame, text="Regresar", command=lambda: self.go_back(tree, path_label))
        back_button.pack(side="bottom", pady=10)
        # Se crea un botón para subir un archivo, llama a la función encargada de subir archivos
        upload_button = tk.Button(self.explorer_frame, text="Subir Archivo", command=lambda: self.subir_archivo(tree), bg="blue", fg="white", font=("Arial", 10))
        upload_button.pack(side="bottom", pady=5)




        tree.bind("<Double-1>", lambda event: self.on_item_click(event, tree, path_label))




        memoria_usada = self.calcular_memoria_explorador()
        hilo = threading.Thread(target=self.hilo_explorador, args=(self.cola_explorador,), daemon=True)
        hilo.start()




        self.procesos_activos["Explorador"] = {"frame": self.explorer_frame, "memoria": memoria_usada, "hilo": hilo, "cola": self.cola_explorador}
        self.desktop_app.actualizar_procesos_activos()


    def update_directory_tree(self,tree, path):
        #Obtiene el usuario actual desde el self.desktop_app y lo pone en la carpeta usuarios
        usuario_actual = self.desktop_app.auth.usuario_actual


        print(usuario_actual)
        path = f"./usuarios/{usuario_actual}"






        #hace la funcion para que el arbol se pare en la carpeta usuarios/test
        tree.delete(*tree.get_children())


        print('direccion')
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
               
                print(item)
                print(item_path)


                #De ahi saca la ruta absoluta y lo agrega en el arbol


                try:
                    tree.insert('', 'end', text=item, values=[item_path])
                except Exception as e:
                    print(f"Error al insertar {item_path}: {e}")
        except PermissionError:
            pass


        print('termina direcciones')








    def calcular_memoria_explorador(self):
        memoria_base = 30
        num_items = len(self.explorer_frame.winfo_children()) * 1
        return memoria_base + num_items


    # Subir archivos en el directorio del usuario
    def subir_archivo(self,tree):
        user_directory = self.cargar_directorio_usuario()
        file_path = filedialog.askopenfilename(filetypes=[("Todos los archivos", "*.*")])




        if file_path:
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(user_directory, file_name)




            try:
                with open(file_path, 'rb') as src_file:
                    with open(dest_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                self.update_directory_tree(tree, user_directory)
                messagebox.showinfo("Subida exitosa", f"Archivo '{file_name}' subido a tu directorio.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo subir el archivo: {e}")


    # Cargar el directorio del usuario
    def cargar_directorio_usuario(self):
        ###########################global usuario_actual
         #Obtiene el usuario actual desde el self.desktop_app y lo pone en la carpeta usuarios
        usuario_actual = self.desktop_app.auth.usuario_actual




        if usuario_actual:
            user_directory = f"./usuarios/{usuario_actual}"
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
            return user_directory


    def cerrar_explorador(self):
        self.cola_explorador.put("cerrar")
        self.explorer_frame.pack_forget()
        if "Explorador" in self.procesos_activos:
            del self.procesos_activos["Explorador"]
        self.desktop_app.actualizar_procesos_activos()








    def on_item_click(self, event, tree, path_label):
        """Navegar al subdirectorio seleccionado en el Treeview."""
        selected_item = tree.selection()[0]
        selected_path = tree.item(selected_item, 'values')[0]






    def go_back(self, tree, path_label):
        current_path = path_label.cget("text")
        parent_path = os.path.dirname(current_path)
        if parent_path:
            self.update_directory_tree(tree, parent_path)
            path_label.config(text=parent_path)




    def hilo_explorador(self, cola):
        while True:
            mensaje = cola.get()
            if mensaje == "cerrar":
                break


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
            frame = self.procesos_activos[proceso]["frame"]
            hilo = self.procesos_activos[proceso]["hilo"]
            cola = self.procesos_activos[proceso]["cola"]


            if frame:
                frame.pack_forget()
            if cola:
                cola.put("cerrar")
            if hilo and hilo.is_alive():
                hilo.join()


            del self.procesos_activos[proceso]
        self.mostrar()


    def ocultar(self):
        self.frame.pack_forget()

class WorldTimeApp:

    def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        # Crear una nueva ventana Toplevel
        self.hora_window = tk.Toplevel(desktop_app.window)
        self.hora_window.title("Hora Mundial")
        self.hora_window.geometry("400x200")  # Ajusta al tamaño deseado
        self.hora_window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.mostrarHoras()

    def mostrarHoras(self):
        # Añade un label con un mensaje
        message_label = tk.Label(self.hora_window, text="¡Bienvenido a la Aplicación de Hora Mundial!", font=("Arial", 16))
        message_label.pack(pady=20)

        # Añadir otro mensaje o información dinámica
        dynamic_label = tk.Label(self.hora_window, text="Aqui se mostrarán las horas del mundo.", font=("Arial", 14))
        dynamic_label.pack(pady=20)

    def on_close(self):
        self.hora_window.destroy()



        """     def __init__(self, desktop_app):
        self.desktop_app = desktop_app
        self.frame = tk.Frame(desktop_app.window, bg="lightgray", width=300, height=200)
        self.cities = ["America/Grand_Turk", "America/Argentina/Buenos_Aires", "Europe/Madrid", "Asia/Tokyo", "Australia/Sydney"]
        self.labels = {}

        for city in self.cities:
            self.labels[city] = tk.Label(self.frame, text=f"Loading time for {city.split('/')[1]}...", bg="lightgray")
            self.labels[city].pack()

        self.stopped = Event()
        self.thread = Thread(target=self.update_times)
        self.thread.start()
        self.desktop_app.procesos_activos["WorldTime"] = {
            "frame": self.frame,
            "memoria": 50,  
            "hilo": self.thread,
            "cola": None  
        } """

    
    def update_times(self):
        retry_delay = 5
        max_retries = 3
        while not self.stopped.is_set():
            try:
                for city in self.cities:
                    response = self.fetch_data(city, max_retries, retry_delay)
                    if response:
                        current_time = response['datetime']
                        self.labels[city].config(text=f"{city.split('/')[1]}: {current_time}")
                    else:
                        self.labels[city].config(text="Failed to load time.")
            except Exception as e:
                print("Unexpected error:", e)
            time.sleep(60)  # Actualiza cada 60 segundos

    def fetch_data(self, city, max_retries, retry_delay):
        for i in range(max_retries):
            try:
                response = requests.get(f"http://worldtimeapi.org/api/timezone/{city}")
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {city}: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Incrementa el tiempo de espera exponencialmente
        return None

    def show(self):
        self.frame.pack(side="right", fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()

    def stop(self):
        self.stopped.set()
        self.thread.join()







if __name__ == "__main__":
    DesktopApp()