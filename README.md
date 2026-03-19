<div align="center">

# 📈 IBEX35 Hadoop Analytics

**Análisis distribuido del mercado bursátil español con MapReduce**

*Procesamiento masivo de cotizaciones del IBEX 35 mediante Apache Hadoop y mrjob*

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Hadoop](https://img.shields.io/badge/Apache%20Hadoop-3.x-66CCFF?style=flat-square&logo=apachehadoop&logoColor=white)
![mrjob](https://img.shields.io/badge/mrjob-0.7%2B-orange?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## Tabla de contenidos

- [Descripción del proyecto](#-descripción-del-proyecto)
- [Arquitectura](#-arquitectura)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Datos](#-datos)
- [Requisitos](#-requisitos)
- [Instalación y configuración](#-instalación-y-configuración)
- [Modo local (desarrollo)](#-modo-local-desarrollo)
- [Modo Hadoop con Docker](#-modo-hadoop-con-docker)
- [Ejercicios — referencia completa](#-ejercicios--referencia-completa)
- [Ejercicios avanzados (join de datasets)](#-ejercicios-avanzados-join-de-datasets)
- [Guardar y exportar resultados](#-guardar-y-exportar-resultados)
- [Resolución de problemas](#-resolución-de-problemas)

---

## 📌 Descripción del proyecto

Este proyecto implementa **10 jobs de MapReduce** sobre el histórico de cotizaciones del índice bursátil **IBEX 35**, cubriendo un año completo de datos de mercado (marzo 2025 – marzo 2026).

Los análisis están diseñados para ejecutarse en **dos modos**:

| Modo | Cuándo usarlo |
|---|---|
| **Local** (`inline` / sin flag) | Desarrollo y pruebas rápidas con un subconjunto de datos |
| **Hadoop** (`-r hadoop`) | Ejecución distribuida real sobre el clúster Docker |

Los 10 análisis se dividen en dos categorías:

- **7 ejercicios obligatorios** — análisis de precios, variaciones y rankings sobre el CSV de cotizaciones diarias.
- **3 ejercicios avanzados** — cruce (*join*) del CSV de cotizaciones con el CSV de datos fundamentales (PER, ROE, EBITDA, sector...).

---

## 🏗 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   CLÚSTER DOCKER                    │
│                                                     │
│  ┌─────────────────┐     ┌──────────────────────┐  │
│  │   namenode-mr   │     │    datanode-mr1       │  │
│  │  (NameNode +    │────▶│    datanode-mr2       │  │
│  │ ResourceManager)│     │    datanode-mr3       │  │
│  └────────┬────────┘     └──────────────────────┘  │
│           │  HDFS + YARN                            │
└───────────┼─────────────────────────────────────────┘
            │
    python3 script.py -r hadoop hdfs:///...
            │
   ┌────────▼────────┐
   │  mrjob  →  Job  │   Map → Shuffle → Reduce
   └─────────────────┘
```

El clúster simula un entorno Big Data real con:
- **1 NameNode** (también actúa como ResourceManager de YARN)
- **3 DataNodes** (también actúan como NodeManagers)
- Factor de replicación HDFS: **3**
- Tamaño de bloque: **64 MB**

---

## 📁 Estructura del repositorio

```
ibex35-hadoop-analytics/
│
├── src/
│   ├── ej1_semanal.py                  # Listado semanal de cotizaciones
│   ├── ej2_mensual.py                  # Listado mensual de cotizaciones
│   ├── ej3_rango.py                    # Rango de fechas personalizado
│   ├── ej4_minmax.py                   # Mín/Máx por día, semana y mes
│   ├── ej5_top5_subida.py              # Top 5 acciones con mayor subida
│   ├── ej6_top5_bajada.py              # Top 5 acciones con mayor bajada
│   ├── ej7_incremento.py               # Acciones con incremento ≥ X%
│   ├── avanzado1_volatilidad_per.py    # Volatilidad anual vs PER
│   ├── avanzado2_roe_rendimiento.py    # ROE vs Revalorización anual
│   └── avanzado3_influencia_sector.py  # Rendimiento medio por sector
│
├── data/
│   └── raw/
│       ├── ibex35_YYYY-MM-DD.csv                    # Cotizaciones diarias
│       ├── ibex35_fundamentales_YYYY-MM-DD.csv      # Datos fundamentales (actual)
│       └── ibex35_fundamentales_2025-MM-DD.csv      # Datos fundamentales (año anterior)
│
├── scripts/
│   ├── yfinance_data.py                # Descarga cotizaciones vía yfinance
│   ├── yfinance_metricas.py            # Descarga datos fundamentales vía yfinance
│   └── ejecutar_todo_hadoop.sh         # Script maestro: lanza los 10 jobs en Hadoop
│
├── requirements.txt
├── compose-hadoop-cluster-mr.yml       # Definición del clúster Docker
└── README.md
```

---

## 📊 Datos

### CSV de cotizaciones (`ibex35_YYYY-MM-DD.csv`)

Contiene **cotizaciones diarias** de las 30 empresas del IBEX 35 durante el último año.

| Campo | Tipo | Descripción |
|---|---|---|
| `empresa` | string | Nombre de la empresa |
| `fecha` | YYYY-MM-DD | Fecha de cotización |
| `ultimo` | float | Precio de cierre |
| `var` | float | Variación absoluta respecto al día anterior |
| `var_pct` | float | Variación porcentual |
| `maximo` | float | Precio máximo intradía |
| `minimo` | float | Precio mínimo intradía |
| `volumen` | int | Volumen negociado |

### CSV de fundamentales (`ibex35_fundamentales_YYYY-MM-DD.csv`)

Contiene **métricas financieras** de cada empresa, descargadas de Yahoo Finance.

| Campo | Tipo | Descripción |
|---|---|---|
| `empresa` | string | Nombre de la empresa |
| `sector` | string | Sector económico |
| `per` | float | Price-to-Earnings ratio |
| `roe` | float | Return on Equity |
| `deuda_equity` | float | Ratio deuda / capital propio |
| `dividend_yield` | float | Rentabilidad por dividendo |
| `market_cap` | int | Capitalización bursátil |
| `ebitda` | float | EBITDA |

### Regenerar los datos

Los datos se pueden actualizar en cualquier momento descargándolos directamente de Yahoo Finance:

```bash
# Cotizaciones diarias (último año)
python scripts/yfinance_data.py

# Datos fundamentales
python scripts/yfinance_metricas.py
```

---

## ✅ Requisitos

### Para modo local

- Python **3.10+**
- pip

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
mrjob
yfinance
pandas
```

### Para modo Hadoop (Docker)

- Docker **20.10+**
- Docker Compose **v2**
- Al menos **16 GB de RAM** disponibles (4 contenedores × 3 GB + sistema)
- Al menos **10 GB de espacio en disco**

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/ibex35-hadoop-analytics.git
cd ibex35-hadoop-analytics
```

### 2. Crear entorno virtual Python

```bash
python3 -m venv venv
source venv/bin/activate      # Linux / macOS
# venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 3. (Solo Hadoop) Crear la red Docker

```bash
docker network create hadoop-cluster-mr
```

### 4. (Solo Hadoop) Levantar el clúster

```bash
docker compose -f compose-hadoop-cluster-mr.yml up -d
```

Verifica que los 4 contenedores están en estado `Up`:

```bash
docker ps
```

Interfaces web disponibles una vez arrancado:

| Interfaz | URL |
|---|---|
| HDFS NameNode | http://localhost:9870 |
| YARN ResourceManager | http://localhost:8088 |

---

## 💻 Modo local (desarrollo)

El modo local ejecuta el job **en tu propia máquina** sin necesidad de Hadoop. Es ideal para probar la lógica con un subconjunto de datos antes de lanzarlo al clúster.

```bash
# Activar entorno virtual
source venv/bin/activate

# Sintaxis general
python3 src/<script>.py [--parámetros] data/raw/<fichero>.csv
```

### Ejemplos rápidos

```bash
# Ejercicio 1 — semana del 17 de marzo de 2026
python3 src/ej1_semanal.py \
    --fecha-referencia 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv

# Ejercicio 3 — rango anual para Bankinter
python3 src/ej3_rango.py \
    --accion Bankinter \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv

# Ejercicio 7 — empresas con incremento ≥ 20% en el año
python3 src/ej7_incremento.py \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    --porcentaje 20 \
    data/raw/ibex35_2026-03-17.csv

# Avanzado 1 — join de dos CSVs (fundamentales + cotizaciones)
python3 src/avanzado1_volatilidad_per.py \
    data/raw/ibex35_fundamentales_2026-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

> **Tip:** Para pruebas rápidas, crea un CSV reducido con las primeras 500 filas:
> ```bash
> head -501 data/raw/ibex35_2026-03-17.csv > data/raw/ibex35_reducido.csv
> ```

---

## 🐳 Modo Hadoop con Docker

### Paso 1 — Arrancar el clúster (cada sesión)

```bash
# Primera vez: levantar (crea los contenedores)
docker compose -f compose-hadoop-cluster-mr.yml up -d

# Sesiones posteriores: arrancar los contenedores ya creados
docker compose -f compose-hadoop-cluster-mr.yml start
```

### Paso 2 — Subir los ficheros al contenedor (solo la primera vez)

Desde tu terminal local (fuera del contenedor):

```bash
# CSVs de datos
docker cp data/raw/ibex35_2026-03-17.csv               namenode-mr:/tmp/
docker cp data/raw/ibex35_fundamentales_2026-03-17.csv namenode-mr:/tmp/
docker cp data/raw/ibex35_fundamentales_2025-03-17.csv namenode-mr:/tmp/

# Scripts Python
docker cp src/ej1_semanal.py            namenode-mr:/home/luser/
docker cp src/ej2_mensual.py            namenode-mr:/home/luser/
docker cp src/ej3_rango.py              namenode-mr:/home/luser/
docker cp src/ej4_minmax.py             namenode-mr:/home/luser/
docker cp src/ej5_top5_subida.py        namenode-mr:/home/luser/
docker cp src/ej6_top5_bajada.py        namenode-mr:/home/luser/
docker cp src/ej7_incremento.py         namenode-mr:/home/luser/
docker cp src/avanzado1_volatilidad_per.py     namenode-mr:/home/luser/
docker cp src/avanzado2_roe_rendimiento.py     namenode-mr:/home/luser/
docker cp src/avanzado3_influencia_sector.py   namenode-mr:/home/luser/
docker cp scripts/ejecutar_todo_hadoop.sh      namenode-mr:/home/luser/
```

### Paso 3 — Entrar al contenedor y configurar HDFS

```bash
# Entrar al namenode
docker exec -ti namenode-mr /bin/bash

# Cambiar al usuario luser
su - luser

# Crear estructura de directorios en HDFS
hdfs dfs -mkdir -p /user/luser/proyecto_final/data
hdfs dfs -mkdir -p /user/luser/proyecto_final/resultados

# Subir los CSVs desde /tmp al HDFS
hdfs dfs -put /tmp/ibex35_2026-03-17.csv               /user/luser/proyecto_final/data/
hdfs dfs -put /tmp/ibex35_fundamentales_2026-03-17.csv /user/luser/proyecto_final/data/
hdfs dfs -put /tmp/ibex35_fundamentales_2025-03-17.csv /user/luser/proyecto_final/data/

# Verificar que los ficheros están en HDFS
hdfs dfs -ls /user/luser/proyecto_final/data/
```

### Paso 4 — Activar el entorno Python dentro del contenedor

```bash
source ~/venv_hadoop/bin/activate

# Verificar mrjob
python3 -c "import mrjob; print('mrjob OK —', mrjob.__version__)"
```

### Paso 5 — Ejecutar todos los jobs de golpe

```bash
chmod +x /home/luser/ejecutar_todo_hadoop.sh
bash /home/luser/ejecutar_todo_hadoop.sh
```

El script maestro:
1. Verifica que los 3 CSVs están en HDFS antes de empezar
2. Ejecuta los 10 jobs en orden
3. Guarda cada resultado en `/home/luser/resultados_proyecto/`
4. Muestra un resumen final con el estado de cada job

### Paso 6 — Copiar los resultados a tu máquina local

Desde tu terminal local (fuera del contenedor):

```bash
docker cp namenode-mr:/home/luser/resultados_proyecto/ ./resultados/
```

### Paso 7 — Apagar el clúster sin perder datos

```bash
# Salir del contenedor
exit   # sale de luser
exit   # sale del contenedor bash

# Parar los contenedores (los datos en HDFS se conservan)
docker compose -f compose-hadoop-cluster-mr.yml stop
```

> ⚠️ **IMPORTANTE:** Usa siempre `stop`, nunca `down` ni `docker rm`.  
> `down` destruye los contenedores y **borra todos los datos del HDFS** permanentemente.

---

## 📋 Ejercicios — referencia completa

> En todos los comandos Hadoop, sustituye `hdfs:///user/luser/proyecto_final/data/` por la ruta donde hayas subido tus CSVs.

---

### Ejercicio 1 — Listado semanal

Dado un día de referencia, calcula el valor inicial, final, máximo y mínimo de cada acción durante esa semana natural (lunes a domingo).

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--fecha-referencia` | Cualquier día de la semana en formato `YYYY-MM-DD` |

**Modo local:**
```bash
python3 src/ej1_semanal.py \
    --fecha-referencia 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej1_output

python3 ej1_semanal.py -r hadoop \
    --fecha-referencia 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej1_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej1_output/part-*
```

**Ejemplo de salida:**
```
"BBVA"       "Valor inicial: 18.10, Valor final: 18.10, Valor maximo: 18.26, Valor minimo: 17.72"
"ACS"        "Valor inicial: 105.80, Valor final: 105.80, Valor maximo: 106.90, Valor minimo: 103.20"
"Inditex"    "Valor inicial: 51.46, Valor final: 51.46, Valor maximo: 51.98, Valor minimo: 51.14"
```

---

### Ejercicio 2 — Listado mensual

Igual que el ejercicio 1 pero para todo el mes al que pertenece la fecha de referencia.

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--fecha-referencia` | Cualquier día del mes en formato `YYYY-MM-DD` |

**Modo local:**
```bash
python3 src/ej2_mensual.py \
    --fecha-referencia 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej2_output

python3 ej2_mensual.py -r hadoop \
    --fecha-referencia 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej2_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej2_output/part-*
```

**Ejemplo de salida:**
```
"BBVA"    "Valor inicial: 18.99, Valor final: 18.10, Valor maximo: 19.38, Valor minimo: 17.58"
"Repsol"  "Valor inicial: 20.08, Valor final: 23.32, Valor maximo: 24.30, Valor minimo: 19.20"
```

---

### Ejercicio 3 — Rango de fechas personalizado

Para una acción y rango de fechas dados, calcula el mínimo y máximo histórico y los porcentajes de decremento e incremento desde el precio inicial.

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--accion` | Nombre de la empresa tal como aparece en el CSV |
| `--fecha-inicio` | Fecha de inicio del rango (`YYYY-MM-DD`) |
| `--fecha-fin` | Fecha de fin del rango (`YYYY-MM-DD`) |

**Modo local:**
```bash
python3 src/ej3_rango.py \
    --accion Bankinter \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej3_output

python3 ej3_rango.py -r hadoop \
    --accion Bankinter \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej3_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej3_output/part-*
```

**Ejemplo de salida:**
```
"Bankinter"  "Valor minimo: 7.43, Valor maximo: 14.99, Decremento: 24.26%, Incremento: 52.80%"
```

---

### Ejercicio 4 — Mín/Máx por período

Para una acción, devuelve el mínimo y máximo de cotización agrupado por tres períodos: día exacto, última semana (7 días) y último mes (30 días) respecto a la fecha de referencia.

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--accion` | Nombre de la empresa |
| `--fecha` | Fecha de referencia (`YYYY-MM-DD`) |

**Modo local:**
```bash
python3 src/ej4_minmax.py \
    --accion Bankinter \
    --fecha 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej4_output

python3 ej4_minmax.py -r hadoop \
    --accion Bankinter \
    --fecha 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej4_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej4_output/part-*
```

**Ejemplo de salida:**
```
"Bankinter"  {
  "ultima_hora":   {"min": null,  "max": null},
  "ultima_semana": {"min": 12.85, "max": 13.85},
  "ultimo_mes":    {"min": 12.67, "max": 14.81}
}
```

---

### Ejercicio 5 — Top 5 acciones que más han subido

Identifica las 5 acciones con mayor revalorización porcentual tanto en la última semana como en el último mes respecto a la fecha de referencia. Implementado con **2 jobs encadenados** (MRStep).

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--fecha` | Fecha de referencia como "hoy" (`YYYY-MM-DD`) |

**Modo local:**
```bash
python3 src/ej5_top5_subida.py \
    --fecha 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej5_output

python3 ej5_top5_subida.py -r hadoop \
    --fecha 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej5_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej5_output/part-*
```

**Ejemplo de salida:**
```
"mes"     ["Repsol: 35.98%", "Indra: 15.62%", "Solaria: 13.19%", "Acciona: 10.77%", "Endesa: 10.27%"]
"semana"  ["Repsol: 4.71%", "Solaria: 4.53%", "Naturgy: 2.15%", "Merlin: 2.13%", "Redeia: 1.82%"]
```

---

### Ejercicio 6 — Top 5 acciones que más han bajado

Simétrico al ejercicio 5 pero ordenando por mayor caída porcentual. Implementado con **2 jobs encadenados**.

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--fecha` | Fecha de referencia como "hoy" (`YYYY-MM-DD`) |

**Modo local:**
```bash
python3 src/ej6_top5_bajada.py \
    --fecha 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej6_output

python3 ej6_top5_bajada.py -r hadoop \
    --fecha 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej6_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej6_output/part-*
```

**Ejemplo de salida:**
```
"mes"     ["IAG: 19.65%", "Grifols: 17.32%", "Almirall: 16.33%", "ArcelorMittal: 16.29%", "Aena: 10.79%"]
"semana"  ["ArcelorMittal: 3.94%", "Amadeus: 2.98%", "IAG: 2.39%", "Inditex: 2.13%", "Acerinox: 1.65%"]
```

---

### Ejercicio 7 — Acciones con incremento superior a un umbral

Dado un porcentaje mínimo y un rango de fechas, devuelve todas las acciones que han superado ese umbral de revalorización, ordenadas de menor a mayor incremento. Implementado con **2 jobs encadenados**.

**Parámetros:**

| Parámetro | Descripción |
|---|---|
| `--fecha-inicio` | Inicio del período (`YYYY-MM-DD`) |
| `--fecha-fin` | Fin del período (`YYYY-MM-DD`) |
| `--porcentaje` | Umbral mínimo de incremento (ej. `20` para ≥ 20%) |

**Modo local:**
```bash
python3 src/ej7_incremento.py \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    --porcentaje 20 \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej7_output

python3 ej7_incremento.py -r hadoop \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    --porcentaje 20 \
    --output-dir /user/luser/proyecto_final/resultados/ej7_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej7_output/part-*
```

**Ejemplo de salida** (umbral 20%, rango anual):
```
"IAG"           "23.56"
"Bankinter"     "31.69"
"Mapfre"        "34.80"
"Ferrovial"     "37.37"
"BBVA"          "46.56"
"Santander"     "52.16"
"Repsol"       "106.74"
"Indra"        "128.00"
"Solaria"      "191.97"
```
*(20 empresas superan el umbral del 20% en el período anual analizado)*

---

## 🔬 Ejercicios avanzados (join de datasets)

Estos tres ejercicios cruzan el CSV de **cotizaciones** con el de **datos fundamentales**, realizando un join distribuido por empresa dentro del propio job de MapReduce. El Mapper detecta el origen del fichero por el formato de sus columnas (fecha en cotizaciones vs. sector/PER en fundamentales) y emite una etiqueta `HIST` o `FUND` que el Reducer usa para unir la información.

---

### Avanzado 1 — Volatilidad anual vs PER

Calcula la volatilidad anual de cada empresa (porcentaje de variación entre el precio máximo y mínimo del año) y la cruza con su PER. Permite analizar si las empresas más caras (PER alto) son también las más volátiles.

**Modo local:**
```bash
python3 src/avanzado1_volatilidad_per.py \
    data/raw/ibex35_fundamentales_2026-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/av1_output

python3 avanzado1_volatilidad_per.py -r hadoop \
    --output-dir /user/luser/proyecto_final/resultados/av1_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2026-03-17.csv \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/av1_output/part-*
```

**Ejemplo de salida:**
```
"IAG"      ["Sector: Industrials",        "PER: 5.87",   "Volatilidad: 104.69%"]
"Naturgy"  ["Sector: Utilities",          "PER: 11.83",  "Volatilidad: 22.29%"]
"Solaria"  ["Sector: Utilities",          "PER: 19.73",  "Volatilidad: 255.50%"]
"Inditex"  ["Sector: Consumer Cyclical",  "PER: 26.97",  "Volatilidad: 43.26%"]
```

> **Conclusión:** El PER es un indicador incompleto sin la volatilidad. IAG tiene un PER de 5.9 (barato en teoría) pero una volatilidad del 104%, lo que hace el cálculo de recuperación de inversión muy poco fiable. Naturgy con PER 11.8 y volatilidad del 22% ofrece una estimación mucho más creíble.

---

### Avanzado 2 — ROE vs Revalorización anual

Cruza el ROE (*Return on Equity*, eficiencia operativa) de cada empresa con su revalorización bursátil real durante el año. Analiza si las empresas más eficientes internamente son también las que más suben en bolsa. Usa el CSV de fundamentales del año anterior para reflejar el ROE que el mercado conocía al inicio del período.

**Modo local:**
```bash
python3 src/avanzado2_roe_rendimiento.py \
    data/raw/ibex35_fundamentales_2025-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/av2_output

python3 avanzado2_roe_rendimiento.py -r hadoop \
    --output-dir /user/luser/proyecto_final/resultados/av2_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2025-03-17.csv \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/av2_output/part-*
```

**Ejemplo de salida:**
```
"Indra"      ["ROE: 25.13%", "Revalorizacion: 132.00%"]
"Repsol"     ["ROE: 7.55%",  "Revalorizacion: 110.85%"]
"Inditex"    ["ROE: 29.81%", "Revalorizacion: 17.95%"]
"Telefonica" ["ROE: -0.25%", "Revalorizacion: -12.10%"]
```

> **Conclusión:** Un ROE alto no garantiza una gran revalorización a corto plazo porque el mercado ya lo ha descontado en el precio. Repsol (ROE modesto del 7.55%) subió un 110% por el alza del petróleo; Indra (ROE del 25%) subió un 132% por contratos de defensa — factores externos, no la eficiencia interna.

---

### Avanzado 3 — Rendimiento medio por sector

Implementado con **2 jobs encadenados**. El primer job cruza los dos CSVs y calcula la revalorización anual de cada empresa. El segundo job agrupa por sector y calcula la media aritmética de las revalorizaciones, permitiendo comparar qué sectores del IBEX han rendido mejor en el año.

**Modo local:**
```bash
python3 src/avanzado3_influencia_sector.py \
    data/raw/ibex35_fundamentales_2026-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

**Modo Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/av3_output

python3 avanzado3_influencia_sector.py -r hadoop \
    --output-dir /user/luser/proyecto_final/resultados/av3_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2026-03-17.csv \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/av3_output/part-*
```

**Ejemplo de salida:**
```
"Energy"                 {"Media revalorizacion": "110.85%",  "Num empresas": 1}
"Technology"             {"Media revalorizacion": "52.80%",   "Num empresas": 2}
"Utilities"              {"Media revalorizacion": "47.53%",   "Num empresas": 7}
"Industrials"            {"Media revalorizacion": "46.17%",   "Num empresas": 7}
"Financial Services"     {"Media revalorizacion": "41.21%",   "Num empresas": 7}
"Consumer Cyclical"      {"Media revalorizacion": "24.96%",   "Num empresas": 2}
"Real Estate"            {"Media revalorizacion": "12.42%",   "Num empresas": 3}
"Healthcare"             {"Media revalorizacion": "6.19%",    "Num empresas": 2}
"Communication Services" {"Media revalorizacion": "-12.10%",  "Num empresas": 1}
```

> **Conclusión:** El sector al que pertenece una empresa es tan importante como la empresa en sí. En 2025-2026, apostar por energía o tecnología habría multiplicado la inversión. El único sector en negativo fue comunicaciones, representado por Telefónica.

---

## 💾 Guardar y exportar resultados

### Opción A — Script maestro (todos los jobs de golpe)

```bash
# Dentro del contenedor como luser, con venv activado
bash /home/luser/ejecutar_todo_hadoop.sh
```

El script guarda automáticamente cada resultado en `/home/luser/resultados_proyecto/` con el nombre `ej<N>_<nombre>.txt`.

### Opción B — Guardado manual

```bash
mkdir -p /home/luser/resultados_proyecto

for ej in ej1 ej2 ej3 ej4 ej5 ej6 ej7 av1 av2 av3; do
    hdfs dfs -cat /user/luser/proyecto_final/resultados/${ej}_output/part-* \
        > /home/luser/resultados_proyecto/${ej}_resultado.txt 2>/dev/null
    echo "✓ $ej guardado"
done
```

### Exportar a tu máquina local

Desde tu terminal local (fuera del contenedor):

```bash
docker cp namenode-mr:/home/luser/resultados_proyecto/ ./resultados/
```

Los ficheros en `./resultados/` son tu copia permanente, independiente de Docker.

---

## 🔧 Resolución de problemas

### `OSError: Input path does not exist`

El error más común. Asegúrate de usar el prefijo `hdfs:///` en las rutas de entrada cuando ejecutas con `-r hadoop`:

```bash
# ❌ Incorrecto
python3 script.py -r hadoop /user/luser/proyecto_final/data/ibex35.csv

# ✅ Correcto
python3 script.py -r hadoop hdfs:///user/luser/proyecto_final/data/ibex35.csv
```

Verifica que el fichero existe en HDFS:
```bash
hdfs dfs -ls /user/luser/proyecto_final/data/
```

### `Output directory already exists`

HDFS no sobreescribe directorios de salida. Bórralo antes de cada ejecución:

```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ejX_output
```

### `ModuleNotFoundError: No module named 'mrjob'`

El entorno virtual no está activado:

```bash
source ~/venv_hadoop/bin/activate
```

### `python3: can't open file '/home/luser/script.py'`

El script no se ha copiado al contenedor. Desde tu terminal local:

```bash
docker cp src/script.py namenode-mr:/home/luser/
```

### El job se queda colgado o no termina

Consulta el estado en la interfaz web de YARN: http://localhost:8088

O desde consola:

```bash
# Ver aplicaciones activas
yarn application -list

# Matar una aplicación colgada
yarn application -kill <application_id>
```

### Problemas de memoria (contenedor muere o job falla)

Verifica que tienes suficiente RAM libre. El clúster necesita ~12 GB:

```bash
docker stats --no-stream
```

Si hay problemas, ajusta los límites de memoria en `compose-hadoop-cluster-mr.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 2048m   # Reducir de 3072m si hay poca RAM
```

---

## 👤 Autor

**Denys Litvynov Lymanets**  
Proyecto de Big Data — Análisis distribuido del IBEX 35  
Curso 2025–2026

---

<div align="center">

*Hecho con Apache Hadoop, mrjob y datos reales de Yahoo Finance*

</div>
