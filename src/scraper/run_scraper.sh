#!/bin/bash

# Ruta al archivo de datos (relativa a donde está el script)
DATA_DIR="../../data/raw"
mkdir -p $DATA_DIR

echo "Iniciando automatizador del IBEX-35..."

while true; do
    HORA_ACTUAL=$(date +%H%M)
    DIA_SEMANA=$(date +%u) # 1=Lunes, 7=Domingo
    FECHA=$(date +%Y-%m-%d)
    FICHERO="$DATA_DIR/ibex35_$FECHA.csv"

    # Comprobamos: Lunes a Viernes (1-5) y entre las 09:00 y las 18:30
    if [ "$DIA_SEMANA" -le 5 ] && [ "$HORA_ACTUAL" -ge 0900 ] && [ "$HORA_ACTUAL" -le 1830 ]; then
        echo "--- Ejecutando extracción: $(date) ---"
        
        # Ejecutamos el scraper y lo añadimos al fichero diario
        # Usamos 'tail -n +2' para no repetir la cabecera si el fichero ya existe
        if [ ! -f "$FICHERO" ]; then
            python3 scraper.py > "$FICHERO"
        else
            python3 scraper.py | tail -n +2 >> "$FICHERO"
        fi

        echo "Datos guardados en $FICHERO"

        # ==========================================================
        # FUTURO: SUBIDA A HDFS
        # Cuando el cluster esté activo, solo habrá que descomentar:
        # docker exec hadoop-namenode hdfs dfs -put -f /ruta/en/contenedor/$FICHERO /user/denys/raw/
        # ==========================================================

        echo "Esperando 1 hora para la siguiente toma..."
        sleep 3600
    else
        echo "Mercado cerrado ($(date +%H:%M)). Reintentando en 15 minutos..."
        sleep 900
    fi
done
