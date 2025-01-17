import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import time
import os
import threading
import csv

# Función para leer actividades desde un archivo
def leer_actividades(nombre_archivo):
    actividades = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                nombre, porcentaje = linea.strip().split(',')
                actividades.append((nombre.strip(), float(porcentaje.strip())))
    except Exception as e:
        messagebox.showerror("Error", f"Error leyendo el archivo: {e}")
    return actividades

# Función para calcular tiempos asignados
def calcular_tiempos(actividades, tiempo_disponible):
    tiempos_asignados = []
    for nombre, porcentaje in actividades:
        tiempo_asignado = (porcentaje / 100) * tiempo_disponible
        tiempos_asignados.append((nombre, round(tiempo_asignado, 2)))
    return tiempos_asignados

# Función para registrar actividades completadas con bloqueo
registro_lock = threading.Lock()
def registrar_actividad(nombre_archivo, actividad, tiempo):
    try:
        with registro_lock:
            with open(nombre_archivo, 'a', newline='') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), actividad, tiempo])
    except Exception as e:
        print(f"Error al registrar la actividad: {e}")

# Función para emitir sonido
def emitir_sonido(nombre_archivo):
    ruta_sonido = os.path.join(os.path.dirname(__file__), nombre_archivo)
    if os.path.exists(ruta_sonido):
        os.system(f"aplay {ruta_sonido} > /dev/null 2>&1")

# Variables de control globales para pausa
pausado = False

# Temporizador
def iniciar_temporizador(actividades, modo_pausa):
    global pausado
    for idx, (actividad, tiempo) in enumerate(actividades):
        tiempo_restante = tiempo * 60  # Convertir minutos a segundos
        progreso_bar['maximum'] = tiempo_restante
        tiempo_para_beep = 300  # 5 minutos en segundos

        while tiempo_restante > 0:
            if pausado:
                status_label.config(text="PAUSA", font=("Arial", 12, "bold"))
                root.update()
                time.sleep(1)
                continue

            minutos, segundos = divmod(tiempo_restante, 60)
            status_label.config(text=f"Tarea: {actividad} - {int(minutos):02d}:{int(segundos):02d}", font=("Arial", 12, "bold"))
            progreso_bar['value'] = tiempo_restante
            root.update()
            time.sleep(1)
            tiempo_restante -= 1

            # Emitir un beep cada 5 minutos
            if tiempo_restante % tiempo_para_beep == 0 and tiempo_restante > 0:
                emitir_sonido("beep.wav")

        emitir_sonido("campana.wav")
        registrar_actividad("registro.csv", actividad, tiempo)

        # Cambiar color de tarea completada
        tareas_list.itemconfig(idx, {'fg': 'gray'})

        if modo_pausa:
            messagebox.showinfo("Tarea completada", f"Tarea '{actividad}' completada. Presione OK para continuar.")

    status_label.config(text="Todas las tareas completadas.", font=("Arial", 12, "bold"))
    progreso_bar['value'] = 0
    emitir_sonido("fin.wav")

# Función para pausar o reanudar
def toggle_pausa():
    global pausado
    pausado = not pausado
    if pausado:
        pausa_button.config(text="Reanudar")
    else:
        pausa_button.config(text="Pausar")

# Función para iniciar la ejecución
def ejecutar():
    archivo = file_var.get()
    if not archivo:
        messagebox.showerror("Error", "Seleccione un archivo de actividades.")
        return

    actividades = leer_actividades(archivo)
    if not actividades:
        messagebox.showerror("Error", "No se pudieron cargar las actividades.")
        return

    try:
        if tiempo_var.get() == "Tiempo disponible":
            tiempo_disponible = int(time_entry.get())
        else:
            hora_actual = datetime.now()
            hora_finalizacion = datetime.strptime(time_entry.get(), "%H:%M").time()
            hora_finalizacion = datetime.combine(hora_actual.date(), hora_finalizacion)
            if hora_finalizacion < hora_actual:
                hora_finalizacion += timedelta(days=1)
            tiempo_disponible = int((hora_finalizacion - hora_actual).total_seconds() / 60)
    except ValueError:
        messagebox.showerror("Error", "Ingrese un valor válido para el tiempo.")
        return

    resultados = calcular_tiempos(actividades, tiempo_disponible)

    # Mostrar las actividades en la interfaz
    tareas_list.delete(0, tk.END)
    for actividad, tiempo in resultados:
        tareas_list.insert(tk.END, f"{actividad}: {tiempo} minutos")

    modo_pausa = pausa_var.get() == 1

    # Iniciar el temporizador en un hilo separado
    threading.Thread(target=iniciar_temporizador, args=(resultados, modo_pausa), daemon=True).start()

# Función para seleccionar archivo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos *.act", "*.act")])
    file_var.set(archivo)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestor de Tiempos")
root.geometry("500x450")

# Establecer icono
ruta_icono = os.path.join(os.path.dirname(__file__), "activ.png")
if os.path.exists(ruta_icono):
    icono = tk.PhotoImage(file=ruta_icono)
    root.iconphoto(True, icono)

# Variables de control
file_var = tk.StringVar()
tiempo_var = tk.StringVar(value="Tiempo disponible")
pausa_var = tk.IntVar(value=1)

# Widgets
file_frame = tk.Frame(root)
file_frame.pack(pady=5)

file_label = tk.Label(file_frame, text="Archivo de actividades:")
file_label.pack(side=tk.LEFT, padx=5)

file_entry = tk.Entry(file_frame, textvariable=file_var, width=30)
file_entry.pack(side=tk.LEFT, padx=5)

file_button = tk.Button(file_frame, text="Seleccionar", command=seleccionar_archivo)
file_button.pack(side=tk.LEFT, padx=5)

time_frame = tk.Frame(root)
time_frame.pack(pady=5)

time_label = tk.Label(time_frame, text="Tiempo o finalización:")

time_label.pack(side=tk.LEFT, padx=5)

time_entry = tk.Entry(time_frame, width=8)
time_entry.pack(side=tk.LEFT, padx=5)

mode_menu = tk.OptionMenu(time_frame, tiempo_var, "Tiempo disponible", "Hora de finalización")
mode_menu.pack(side=tk.LEFT, padx=5)

pausa_check = tk.Checkbutton(root, text="Pausas", variable=pausa_var)
pausa_check.pack(pady=5)

tareas_frame = tk.Frame(root)
tareas_frame.pack(pady=5)

scrollbar = tk.Scrollbar(tareas_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tareas_list = tk.Listbox(tareas_frame, height=8, width=40, yscrollcommand=scrollbar.set)
tareas_list.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=tareas_list.yview)

buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=5)

start_button = tk.Button(buttons_frame, text="Iniciar", command=ejecutar)
start_button.pack(side=tk.LEFT, padx=5)

pausa_button = tk.Button(buttons_frame, text="Pausar", command=toggle_pausa)
pausa_button.pack(side=tk.LEFT, padx=5)

status_label = tk.Label(root, text="Seleccione un archivo y configure el tiempo.")
status_label.pack(pady=5)

progreso_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progreso_bar.pack(pady=5)

root.mainloop()
