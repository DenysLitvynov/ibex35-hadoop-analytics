📈 IBEX35 Big Data Analytics (Hadoop + MapReduce)

Este proyecto permite realizar un análisis profundo de las cotizaciones del IBEX 35 utilizando el paradigma MapReduce sobre un clúster de Hadoop (Dockerizado). Incluye desde análisis semanales básicos hasta estudios avanzados de correlación entre volatilidad y datos fundamentales (PER, ROE).
🛠️ 1. Pruebas en Local (Quick Start)

Antes de subir el código al clúster, puedes probar los scripts de Python localmente para verificar que la lógica de Map y Reduce es correcta.
Requisitos previos

    Python 3.x

    Instalar la librería mrjob:
    Bash

    pip install mrjob

Ejecución local

Para probar cualquier ejercicio sin necesidad de Hadoop:
Bash

python scripts/ejercicio_X.py datos/archivo.csv

Ejemplo para el Ejercicio 1:
Bash

python ej1_semanal.py --fecha-referencia 2026-03-17 data/ibex35_2026-03-17.csv

🚀 2. Despliegue Completo en Hadoop

Sigue estos pasos para ejecutar el análisis en un entorno distribuido real.
Paso A: Levantar el Clúster

Utiliza los alias configurados para gestionar los contenedores de Docker:
Bash

hadoop-up    # Levanta los nodos: Namenode, Datanode, ResourceManager y NodeManager

Paso B: Preparación del Entorno (HDFS)

    Acceder al contenedor maestro:
    Bash

    docker exec -it namenode-mr /bin/bash

    Subir los datos a HDFS:
    Hadoop no lee archivos de tu disco duro directamente; deben estar en su sistema de archivos (HDFS):
    Bash

    hdfs dfs -mkdir -p /user/luser/proyecto/data
    hdfs dfs -put /ruta/local/tus_datos.csv /user/luser/proyecto/data/

Paso C: Ejecución Automatizada

El proyecto incluye un Script Maestro (ejecutar_todo_hadoop.sh) que lanza los 10 ejercicios de forma secuencial:
Bash

# Dentro del contenedor, con el venv activo
bash ejecutar_todo_hadoop.sh

Paso D: Recuperación de Resultados

Los resultados se generan en HDFS, pero para analizarlos o entregarlos debemos bajarlos al "mundo real":

    De HDFS al Contenedor:
    Bash

    hdfs dfs -get /user/luser/proyecto/resultados/ej_output/part-* ./resultado_ej.txt

    Del Contenedor a tu Ordenador (Desde tu terminal local):
    Bash

    docker cp namenode-mr:/home/luser/resultado_ej.txt ./mis_resultados/

📊 Ejercicios Incluidos
Nivel	Descripción
Básico	Listados semanales/mensuales, rangos de cotización y Top 5 (subidas/bajadas).
Avanzado 1	Volatilidad vs PER: Relación entre el riesgo y la valoración de la empresa.
Avanzado 2	ROE vs Rendimiento: Eficiencia operativa interna frente a éxito bursátil.
Avanzado 3	Análisis Sectorial: Comparativa de crecimiento por sectores industriales.
🛑 Apagado Seguro

Para evitar la pérdida de datos en HDFS, nunca uses down. Usa el alias de stop:
Bash

hadoop-down

    Nota: Esto detiene los contenedores pero mantiene el estado del disco virtual de Hadoop intacto para la próxima sesión.
