import tkinter as tk
import time
import os


# Vector (lista) para almacenar los procesos activos
procesos_activos = []


# Función para actualizar la hora
def update_clock():
    current_time = time.strftime('%I:%M %p')
    clock_label.config(text=current_time)
    window.after(1000, update_clock)


# Función para mostrar/ocultar el menú de inicio
def toggle_menu():
    if menu_frame.winfo_ismapped():  # Si el menú está visible, lo ocultamos
        menu_frame.pack_forget()
    else:
        menu_frame.pack(side="left", anchor="sw", padx=1, pady=(0, 1))  # Mostrar el menú


# Función para cambiar a la pantalla de escritorio
def show_desktop():
    welcome_frame.pack_forget()  # Oculta la pantalla de bienvenida
    taskbar.pack(side="bottom", fill="x")  # Muestra la barra de tareas y demás elementos del escritorio
    update_clock()  # Iniciar la actualización del reloj


# Función para abrir una aplicación y agregarla a los procesos activos
def abrir_aplicacion(nombre_aplicacion):
    #if nombre_aplicacion not in procesos_activos:
    procesos_activos.append(nombre_aplicacion)
    actualizar_procesos_activos()
    print(f"Aplicación '{nombre_aplicacion}' abierta. Procesos activos: {procesos_activos}")


# Función para actualizar la lista de procesos activos en la interfaz del administrador de tareas
def actualizar_procesos_activos():
    for widget in task_manager_frame.winfo_children():
        widget.destroy()  # Limpiar el contenido actual

    tk.Label(task_manager_frame, text="Procesos Activos:", font=("Arial", 12, "bold")).pack(pady=5)
    
    for proceso in procesos_activos:
        tk.Label(task_manager_frame, text=proceso, font=("Arial", 10)).pack(anchor="w", padx=10)
    
    # Agregar un botón para cerrar el administrador de tareas
    cerrar_button = tk.Button(task_manager_frame, text="Cerrar Administrador", command=toggle_task_manager)
    cerrar_button.pack(pady=10)


# Función para mostrar/ocultar el administrador de tareas
def toggle_task_manager():
    if task_manager_frame.winfo_ismapped():
        task_manager_frame.pack_forget()  # Ocultar el administrador de tareas
    else:
        actualizar_procesos_activos()
        task_manager_frame.pack(side="right", fill="y", padx=5, pady=5)  # Mostrar el administrador de tareas
# Función para cerrar el programa
def apagar():
    window.destroy()  # Cierra la ventana principal y termina el programa

# Crear la ventana principal
window = tk.Tk()
window.title("Simulación de Escritorio Windows")
window.geometry("800x600")
window.config(bg="lightblue")


# Pantalla de bienvenida
welcome_frame = tk.Frame(window, bg="white")
welcome_frame.pack(fill="both", expand=True)

welcome_label = tk.Label(welcome_frame, text="Bienvenido", font=("Arial", 24), bg="white")
welcome_label.pack(pady=50)

# se carga el logo por medio del os de pyhton
logo = tk.PhotoImage(file=os.path.join(os.getcwd(), "images/s1.png"))

logo_label = tk.Label(welcome_frame, image=logo, bg="white")
logo_label.pack(pady=50)

# Botón para ingresar
enter_button = tk.Button(welcome_frame, text="Ingresar", font=("Arial", 14), command=show_desktop)
enter_button.pack(pady=20)


# Configuración de la pantalla del escritorio (inicialmente no visible)
# Crear la barra de tareas en la parte inferior
taskbar = tk.Frame(window, bg="gray", height=20)

# Botón "Inicio" en la barra de tareas inferior
start_button = tk.Button(taskbar, text="Menú", width=10, height=2, bg="#0078D7", fg="white", font=("Arial", 10, "bold"), command=toggle_menu)
start_button.pack(side="left", padx=0, pady=0)

# Contenedor para el menú de inicio (inicialmente no visible)
menu_frame = tk.Frame(window, bg="white", width=300, height=600, relief="solid", bd=1)

# Crear botones de menú en formato de lista vertical
programs = ["Explorador", "Archivos", "Ajustes", "Apagar", "Tabla control"]
for program in programs:
    if program == "Tabla control":
        button = tk.Button(menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=toggle_task_manager)
    elif program == "Apagar":
        button = tk.Button(menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=apagar)
    else:
        button = tk.Button(menu_frame, text=program, width=15, height=2, bg="lightgray", relief="groove", command=lambda p=program: abrir_aplicacion(p))
    button.pack(pady=1, padx=1, anchor="w")  # Alineación a la izquierda


# Reloj en la barra de tareas
clock_label = tk.Label(taskbar, bg="gray", fg="white", font=("Arial", 12))
clock_label.pack(side="right", padx=10)

# Contenedor del Administrador de Tareas (inicialmente no visible)
task_manager_frame = tk.Frame(window, bg="white", width=200, relief="solid", bd=1)

# Bucle principal de la aplicación
window.mainloop()
