#!/bin/bash
cp /tmp/crimes_2021.csv /tmp/crimes_2020.csv
hdfs dfs -mkdir -p crimes_filtered
for file in /tmp/crimes_2017.csv /tmp/crimes_2018.csv /tmp/crimes_2019.csv /tmp/crimes_2020.csv; do
    year=$(echo $file | grep -oE '[0-9]{4}' | head -1)
    output="crimes_${year}_filtered.csv"
    # Filtrar por calles de streets.txt y seleccionar columnas 3,4,8,11
    grep -f /tmp/streets.txt $file | awk -F',' '{print $3","$4","$8","$11}' > /tmp/$output
    # Crear carpeta en HDFS y subir
    hdfs dfs -mkdir -p crimes_filtered/$year
    hdfs dfs -put /tmp/$output crimes_filtered/$year/
    # Mostrar conteo Harassment sobre el nuevo fichero
    h_count=$(grep -i "Harassment" /tmp/$output | wc -l)
    echo "Año $year (Filtrado) - Harassment: $h_count"
done
