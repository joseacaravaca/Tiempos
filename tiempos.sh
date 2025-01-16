#!/bin/bash

# Ruta completa al archivo Tiempos.py
RUTA_SCRIPT="/home/jacv/Python/Proyectos/Tiempos/tiempos_ui.py"

# Verificar si el archivo existe
if [ ! -f "$RUTA_SCRIPT" ]; then
    echo "El archivo Tiempos.py no se encontró en la ruta especificada: $RUTA_SCRIPT"
    exit 1
fi

# Abrir ejecutar el script
python3 "$RUTA_SCRIPT"