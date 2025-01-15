import csv
from datetime import datetime, timedelta
import time
import os
import platform

# Función para listar y seleccionar un archivo de actividades
def seleccionar_archivo():
    archivos = [f for f in os.listdir('.') if f.startswith('act_') and f.endswith('.txt')]
    if not archivos:
        print("No se encontraron archivos que comiencen con 'act_' en el directorio actual.")
        return None

    print("Archivos disponibles:")
    for i, archivo in enumerate(archivos, 1):
        print(f"{i}. {archivo}")

    try:
        seleccion = int(input("Seleccione un archivo por su número: "))
        if 1 <= seleccion <= len(archivos):
            return archivos[seleccion - 1]
        else:
            print("Selección inválida.")
            return seleccionar_archivo()
    except ValueError:
        print("Entrada inválida. Intente de nuevo.")
        return seleccionar_archivo()

# Función para leer actividades y porcentajes desde un archivo de texto
def leer_actividades(nombre_archivo):
    actividades = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                nombre, porcentaje = linea.strip().split(',')
                actividades.append((nombre.strip(), float(porcentaje.strip())))
        return actividades
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
        return []

# Función para calcular tiempos asignados
def calcular_tiempos(actividades, tiempo_disponible):
    tiempos_asignados = []
    for nombre, porcentaje in actividades:
        tiempo_asignado = (porcentaje / 100) * tiempo_disponible
        tiempos_asignados.append((nombre, round(tiempo_asignado, 2)))
    return tiempos_asignados

# Función para guardar resultados en un archivo CSV
def guardar_resultados_csv(nombre_archivo, resultados):
    try:
        with open(nombre_archivo, 'w', newline='') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Nombre Actividad", "Tiempo Asignado (minutos)"])
            escritor.writerows(resultados)
        print(f"Resultados guardados en {nombre_archivo}")
    except Exception as e:
        print(f"Error guardando el archivo CSV: {e}")

# Solicitar tiempo disponible o hora de finalización
def obtener_tiempo_disponible():
    opcion = input("¿Desea ingresar el tiempo disponible en minutos (1) o la hora de finalización (2)? Escriba 1 o 2: ")
    if opcion == '1':
        tiempo_disponible = int(input("Ingrese el tiempo disponible en minutos: "))
    elif opcion == '2':
        hora_actual = datetime.now()
        hora_finalizacion = input("Ingrese la hora de finalización (HH:MM): ")
        try:
            hora_finalizacion = datetime.strptime(hora_finalizacion, '%H:%M').time()
            hora_finalizacion = datetime.combine(hora_actual.date(), hora_finalizacion)
            if hora_finalizacion < hora_actual:
                hora_finalizacion += timedelta(days=1)  # Ajuste si es al día siguiente
            tiempo_disponible = int((hora_finalizacion - hora_actual).total_seconds() / 60)
        except ValueError:
            print("Formato de hora inválido. Intente de nuevo.")
            return obtener_tiempo_disponible()
    else:
        print("Opción no válida. Intente de nuevo.")
        return obtener_tiempo_disponible()
    return tiempo_disponible

# Función para leer el archivo CSV de resultados
def leer_resultados_csv(nombre_archivo):
    actividades = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            lector = csv.reader(archivo)
            next(lector)  # Saltar la cabecera
            for fila in lector:
                actividades.append((fila[0], float(fila[1])))
        return actividades
    except Exception as e:
        print(f"Error leyendo el archivo CSV: {e}")
        return []

# Función para emitir un sonido de campana
def emitir_sonido(nombre_archivo):
    ruta_sonido = os.path.join(os.path.dirname(__file__), nombre_archivo)
    if os.path.exists(ruta_sonido):
        os.system(f"aplay {ruta_sonido} > /dev/null 2>&1")
    else:
        print(f"Archivo de sonido '{nombre_archivo}' no encontrado.")

# Función para iniciar el temporizador de actividades
def iniciar_temporizador(actividades, modo_pausa):
    print("\nActividades y tiempos asignados:")
    for actividad, tiempo in actividades:
        print(f"- {actividad}: {tiempo} minutos")

    input("\nPresione ENTER cuando esté listo para comenzar...")

    for actividad, tiempo in actividades:
        print(f"\nIniciando tarea: {actividad} (Duración: {tiempo} minutos)")
        tiempo_restante = tiempo * 60  # Convertir minutos a segundos
        tiempo_para_beep = 300  # 5 minutos en segundos
        while tiempo_restante > 0:
            minutos, segundos = divmod(int(tiempo_restante), 60)
            print(f"{actividad}: {minutos:02d}:{segundos:02d} restantes", end="\r")
            time.sleep(1)
            tiempo_restante -= 1

            # Emitir un beep cada 5 minutos
            if tiempo_restante % tiempo_para_beep == 0 and tiempo_restante > 0:
                emitir_sonido("beep.wav")

        print(f"\nTarea {actividad} completada.")
        emitir_sonido("campana.wav")

        if modo_pausa:
            input("Presione ENTER para continuar con la siguiente tarea...")

# Programa principal
def main():
    archivo_actividades = seleccionar_archivo()
    if not archivo_actividades:
        return

    actividades = leer_actividades(archivo_actividades)
    if not actividades:
        print("No se encontraron actividades o hubo un error al leerlas.")
        return

    tiempo_disponible = obtener_tiempo_disponible()
    resultados = calcular_tiempos(actividades, tiempo_disponible)

    archivo_resultados = "resultados.csv"
    guardar_resultados_csv(archivo_resultados, resultados)

    # Leer las actividades desde el archivo CSV generado
    actividades_csv = leer_resultados_csv(archivo_resultados)
    if actividades_csv:
        modo_pausa = input("¿Desea ejecutar con pausas entre tareas (S/N)? ").strip().lower() == 's'
        iniciar_temporizador(actividades_csv, modo_pausa)

if __name__ == "__main__":
    main()
