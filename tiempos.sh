#!/bin/bash

# Ruta completa al archivo Tiempos.py
RUTA_SCRIPT="/home/jacv/Python/Proyectos/Tiempos/tiempos.py"

# Verificar si el archivo existe
if [ ! -f "$RUTA_SCRIPT" ]; then
    echo "El archivo Tiempos.py no se encontró en la ruta especificada: $RUTA_SCRIPT"
    exit 1
fi

# Abrir un terminal y ejecutar el script
konsole --noclose -e python3 "$RUTA_SCRIPT"