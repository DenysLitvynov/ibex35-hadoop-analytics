#!/bin/bash
FECHA=$(date +%Y-%m-%d)
echo "Ejecutando extracción manual de prueba..."
python3 scraper.py >> ../../data/raw/ibex35_$FECHA.csv
echo "Hecho. Revisa la carpeta data/raw"
