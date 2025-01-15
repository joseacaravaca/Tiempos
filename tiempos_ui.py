import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from datetime import datetime, timedelta
import time
import os
import threading

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

# Función para emitir sonido
def emitir_sonido(nombre_archivo):
    ruta_sonido = os.path.join(os.path.dirname(__file__), nombre_archivo)
    if os.path.exists(ruta_sonido):
        os.system(f"aplay {ruta_sonido} > /dev/null 2>&1")

# Temporizador
def iniciar_temporizador(actividades, modo_pausa):
    for actividad, tiempo in actividades:
        tiempo_restante = tiempo * 60  # Convertir minutos a segundos
        while tiempo_restante > 0:
            minutos, segundos = divmod(tiempo_restante, 60)
            status_label.config(text=f"Tarea actual: {actividad} - Tiempo restante: {int(minutos):02d}:{int(segundos):02d}")
            root.update()
            time.sleep(1)
            tiempo_restante -= 1

        emitir_sonido("campana.wav")
        if modo_pausa:
            messagebox.showinfo("Tarea completada", f"Tarea '{actividad}' completada. Presione OK para continuar.")

    status_label.config(text="Todas las tareas han sido completadas.")
    emitir_sonido("campana.wav")

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

    # Guardar resultados en CSV
    with open("resultados.csv", 'w', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["Nombre Actividad", "Tiempo Asignado (minutos)"])
        escritor.writerows(resultados)

    # Mostrar las actividades en la interfaz
    tareas_list.delete(0, tk.END)
    for actividad, tiempo in resultados:
        tareas_list.insert(tk.END, f"{actividad}: {tiempo} minutos")

    modo_pausa = pausa_var.get() == 1

    # Iniciar el temporizador en un hilo separado
    threading.Thread(target=iniciar_temporizador, args=(resultados, modo_pausa), daemon=True).start()

# Función para seleccionar archivo
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    file_var.set(archivo)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestor de Tiempos")
root.geometry("600x400")

# Variables de control
file_var = tk.StringVar()
tiempo_var = tk.StringVar(value="Tiempo disponible")
pausa_var = tk.IntVar(value=1)

# Widgets
file_frame = tk.Frame(root)
file_frame.pack(pady=10)

file_label = tk.Label(file_frame, text="Archivo de actividades:")
file_label.pack(side=tk.LEFT, padx=5)

file_entry = tk.Entry(file_frame, textvariable=file_var, width=40)
file_entry.pack(side=tk.LEFT, padx=5)

file_button = tk.Button(file_frame, text="Seleccionar", command=seleccionar_archivo)
file_button.pack(side=tk.LEFT, padx=5)

time_frame = tk.Frame(root)
time_frame.pack(pady=10)

time_label = tk.Label(time_frame, text="Tiempo disponible o hora de finalización:")
time_label.pack(side=tk.LEFT, padx=5)

time_entry = tk.Entry(time_frame, width=10)
time_entry.pack(side=tk.LEFT, padx=5)

mode_menu = tk.OptionMenu(time_frame, tiempo_var, "Tiempo disponible", "Hora de finalización")
mode_menu.pack(side=tk.LEFT, padx=5)

pausa_check = tk.Checkbutton(root, text="Pausas entre tareas", variable=pausa_var)
pausa_check.pack(pady=10)

tareas_frame = tk.Frame(root)
tareas_frame.pack(pady=10)

scrollbar = tk.Scrollbar(tareas_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tareas_list = tk.Listbox(tareas_frame, height=10, width=50, yscrollcommand=scrollbar.set)
tareas_list.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=tareas_list.yview)

start_button = tk.Button(root, text="Iniciar", command=ejecutar)
start_button.pack(pady=10)

status_label = tk.Label(root, text="Seleccione un archivo y configure el tiempo para comenzar.")
status_label.pack(pady=10)

root.mainloop()
