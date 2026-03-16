#!/bin/bash

# Ruta a la carpeta de datos
DATA_DIR="../../data/raw"
mkdir -p $DATA_DIR

echo "Iniciando automatizador del IBEX-35..."

while true; do
    HORA_ACTUAL=$(date +%H%M)
    DIA_SEMANA=$(date +%u) # 1=Lunes, 5=Viernes
    FECHA=$(date +%Y-%m-%d)
    FICHERO="$DATA_DIR/ibex35_$FECHA.csv"

    # Horario de mercado: Lunes a Viernes de 09:00 a 18:30
    if [ "$DIA_SEMANA" -le 5 ] && [ "$HORA_ACTUAL" -ge 0900 ] && [ "$HORA_ACTUAL" -le 1830 ]; then
        echo "--- Ejecutando extracción: $(date) ---"
        
        # IMPORTANTE: Usamos el python del entorno virtual (venv)
        if [ ! -f "$FICHERO" ]; then
            # Si es el primer registro del día, añadimos cabecera (opcional)
            echo "Valor,Ultimo,Var,VarPct,Max,Min,Vol,Cap" > "$FICHERO"
            ../../venv/bin/python3 scraper.py >> "$FICHERO"
        else
            # Si ya existe, añadimos los datos debajo
            ../../venv/bin/python3 scraper.py >> "$FICHERO"
        fi

        echo "Datos guardados en $FICHERO"
        echo "Esperando 1 hora para la siguiente toma..."
        sleep 3600
    else
        echo "Mercado cerrado ($(date +%H:%M)). Reintentando en 15 minutos..."
        sleep 900
    fi
done
