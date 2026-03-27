<div align="center">

# IBEX35 Hadoop Analytics

**Distributed market analysis of the Spanish stock exchange using MapReduce**

*High-throughput processing of IBEX 35 historical price data over Apache Hadoop*

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Hadoop](https://img.shields.io/badge/Apache%20Hadoop-3.x-66CCFF?style=flat-square&logo=apachehadoop&logoColor=white)
![mrjob](https://img.shields.io/badge/mrjob-0.7%2B-orange?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## Table of contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Repository structure](#-repository-structure)
- [Datasets](#-datasets)
- [Requirements](#-requirements)
- [Setup](#-setup)
- [Running locally](#-running-locally)
- [Running on Hadoop](#-running-on-hadoop)
- [Modules — full reference](#-modules--full-reference)
- [Advanced modules — multi-dataset joins](#-advanced-modules--multi-dataset-joins)
- [Persisting results](#-persisting-results)
- [Troubleshooting](#-troubleshooting)
- [Author](#-author)

---

## 📌 Overview

**IBEX35 Hadoop Analytics** is a distributed data processing pipeline that performs financial analysis over a full year of daily closing prices for all 30 companies of the **IBEX 35** index, from March 2025 to March 2026.

The system is built on **Apache Hadoop MapReduce** and the **mrjob** Python framework, and ships with a Docker-based cluster that mirrors a real multi-node Big Data deployment. All components run in two modes without any code changes:

| Mode | Use case |
|---|---|
| **Local** | Development and fast iteration on a workstation |
| **Hadoop** (`-r hadoop`) | Distributed execution across the full Docker cluster |

The pipeline covers **10 analytical modules** split into two categories:

- **7 core modules** — price, variation, and ranking analysis over the daily price dataset.
- **3 advanced modules** — distributed join between the price dataset and a fundamentals dataset (P/E ratio, ROE, EBITDA, sector classification).

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  DOCKER CLUSTER                     │
│                                                     │
│  ┌─────────────────┐     ┌──────────────────────┐  │
│  │   namenode-mr   │     │    datanode-mr1       │  │
│  │  (NameNode +    │────▶│    datanode-mr2       │  │
│  │ ResourceManager)│     │    datanode-mr3       │  │
│  └────────┬────────┘     └──────────────────────┘  │
│           │  HDFS + YARN                            │
└───────────┼─────────────────────────────────────────┘
            │
    python3 module.py -r hadoop hdfs:///...
            │
   ┌────────▼────────┐
   │  mrjob  →  Job  │   Map → Shuffle → Reduce
   └─────────────────┘
```

The cluster simulates a production Big Data deployment:

- **1 NameNode** — also acts as YARN ResourceManager
- **3 DataNodes** — also act as YARN NodeManagers
- HDFS replication factor: **3**
- Block size: **64 MB**

---

## 📁 Repository structure

```
ibex35-hadoop-analytics/
│
├── src/
│   ├── ej1_semanal.py                   # Weekly price summary
│   ├── ej2_mensual.py                   # Monthly price summary
│   ├── ej3_rango.py                     # Custom date-range analysis
│   ├── ej4_minmax.py                    # Min/Max by day, week and month
│   ├── ej5_top5_subida.py               # Top 5 best-performing stocks
│   ├── ej6_top5_bajada.py               # Top 5 worst-performing stocks
│   ├── ej7_incremento.py                # Stocks above a growth threshold
│   ├── avanzado1_volatilidad_per.py     # Annual volatility vs P/E ratio
│   ├── avanzado2_roe_rendimiento.py     # ROE vs annual price return
│   └── avanzado3_influencia_sector.py   # Average return by sector
│
├── data/
│   └── raw/
│       ├── ibex35_2026-03-17.csv
│       ├── ibex35_fundamentales_2026-03-17.csv
│       └── ibex35_fundamentales_2025-03-17.csv
│
├── scripts/
│   ├── yfinance_data.py                 # Downloads daily prices via yfinance
│   ├── yfinance_metricas.py             # Downloads fundamentals via yfinance
│   └── ejecutar_todo_hadoop.sh          # Master script: runs all 10 jobs on Hadoop
│
├── requirements.txt
├── compose-hadoop-cluster-mr.yml
└── README.md
```

---

## 📊 Datasets

### Daily prices — `ibex35_YYYY-MM-DD.csv`

Daily closing price data for all 30 IBEX 35 companies over a full calendar year.

| Field | Type | Description |
|---|---|---|
| `empresa` | string | Company name |
| `fecha` | YYYY-MM-DD | Trading date |
| `ultimo` | float | Closing price |
| `var` | float | Absolute change from previous day |
| `var_pct` | float | Percentage change from previous day |
| `maximo` | float | Intraday high |
| `minimo` | float | Intraday low |
| `volumen` | int | Trading volume |

### Fundamentals — `ibex35_fundamentales_YYYY-MM-DD.csv`

Financial metrics per company sourced from Yahoo Finance.

| Field | Type | Description |
|---|---|---|
| `empresa` | string | Company name |
| `sector` | string | Economic sector |
| `per` | float | Price-to-Earnings ratio |
| `roe` | float | Return on Equity |
| `deuda_equity` | float | Debt-to-equity ratio |
| `dividend_yield` | float | Dividend yield |
| `market_cap` | int | Market capitalisation |
| `ebitda` | float | EBITDA |

### Refreshing the data

Both datasets can be regenerated at any time:

```bash
python scripts/yfinance_data.py       # Fetches the last 365 days of prices
python scripts/yfinance_metricas.py   # Fetches current fundamentals
```

---

## ✅ Requirements

### Local mode

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

### Hadoop mode

- Docker **20.10+**
- Docker Compose **v2**
- At least **16 GB of RAM** available (4 containers × 3 GB + OS headroom)
- At least **10 GB of free disk space**

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/denyslitvynov/ibex35-hadoop-analytics.git
cd ibex35-hadoop-analytics
```

### 2. Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. (Hadoop only) Create the Docker network

```bash
docker network create hadoop-cluster-mr
```

### 4. (Hadoop only) Start the cluster

```bash
docker compose -f compose-hadoop-cluster-mr.yml up -d
```

Confirm all four containers are running:

```bash
docker ps
```

Web interfaces available once the cluster is up:

| Interface | URL |
|---|---|
| HDFS NameNode | http://localhost:9870 |
| YARN ResourceManager | http://localhost:8088 |

---

## 💻 Running locally

The local mode runs every job in-process on the host machine. No Hadoop installation is required.

```bash
source venv/bin/activate

# General syntax
python3 src/<module>.py [--parameters] data/raw/<file>.csv
```

Quick examples:

```bash
# Weekly summary — week of 17 March 2026
python3 src/ej1_semanal.py \
    --fecha-referencia 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv

# Custom date range — Bankinter over one full year
python3 src/ej3_rango.py \
    --accion Bankinter \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv

# Stocks with ≥ 20% growth over the year
python3 src/ej7_incremento.py \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    --porcentaje 20 \
    data/raw/ibex35_2026-03-17.csv

# Advanced join — fundamentals + prices (two input files)
python3 src/avanzado1_volatilidad_per.py \
    data/raw/ibex35_fundamentales_2026-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

---

## 🐳 Running on Hadoop

### Step 1 — Start the cluster

```bash
# First run: create and start containers
docker compose -f compose-hadoop-cluster-mr.yml up -d

# Subsequent runs: start existing containers
docker compose -f compose-hadoop-cluster-mr.yml start
```

### Step 2 — Copy datasets and scripts into the container

Run the following from the host machine:

```bash
# Datasets
docker cp data/raw/ibex35_2026-03-17.csv               namenode-mr:/tmp/
docker cp data/raw/ibex35_fundamentales_2026-03-17.csv namenode-mr:/tmp/
docker cp data/raw/ibex35_fundamentales_2025-03-17.csv namenode-mr:/tmp/

# Analysis modules
docker cp src/ej1_semanal.py                   namenode-mr:/home/luser/
docker cp src/ej2_mensual.py                   namenode-mr:/home/luser/
docker cp src/ej3_rango.py                     namenode-mr:/home/luser/
docker cp src/ej4_minmax.py                    namenode-mr:/home/luser/
docker cp src/ej5_top5_subida.py               namenode-mr:/home/luser/
docker cp src/ej6_top5_bajada.py               namenode-mr:/home/luser/
docker cp src/ej7_incremento.py                namenode-mr:/home/luser/
docker cp src/avanzado1_volatilidad_per.py     namenode-mr:/home/luser/
docker cp src/avanzado2_roe_rendimiento.py     namenode-mr:/home/luser/
docker cp src/avanzado3_influencia_sector.py   namenode-mr:/home/luser/
docker cp scripts/ejecutar_todo_hadoop.sh      namenode-mr:/home/luser/
```

### Step 3 — Connect to the cluster and load data into HDFS

```bash
# Open a shell on the namenode
docker exec -ti namenode-mr /bin/bash

# Switch to luser
su - luser

# Create the project directory structure in HDFS
hdfs dfs -mkdir -p /user/luser/proyecto_final/data
hdfs dfs -mkdir -p /user/luser/proyecto_final/resultados

# Upload datasets from the container's /tmp into HDFS
hdfs dfs -put /tmp/ibex35_2026-03-17.csv               /user/luser/proyecto_final/data/
hdfs dfs -put /tmp/ibex35_fundamentales_2026-03-17.csv /user/luser/proyecto_final/data/
hdfs dfs -put /tmp/ibex35_fundamentales_2025-03-17.csv /user/luser/proyecto_final/data/

# Verify
hdfs dfs -ls /user/luser/proyecto_final/data/
```

### Step 4 — Activate the Python environment inside the container

```bash
source ~/venv_hadoop/bin/activate

# Verify mrjob is available
python3 -c "import mrjob; print('mrjob', mrjob.__version__, '— OK')"
```

### Step 5 — Run all modules at once

```bash
chmod +x /home/luser/ejecutar_todo_hadoop.sh
bash /home/luser/ejecutar_todo_hadoop.sh
```

The master script:
1. Verifies that all three CSV files are present in HDFS before starting
2. Runs all 10 jobs sequentially
3. Saves each output to `/home/luser/resultados_proyecto/`
4. Prints a summary of each job's status on completion

### Step 6 — Export results to the host machine

From the host terminal:

```bash
docker cp namenode-mr:/home/luser/resultados_proyecto/ ./resultados/
```

### Step 7 — Shut down the cluster safely

```bash
# Exit the container
exit   # exits luser
exit   # exits the bash session

# Stop (not destroy) the containers
docker compose -f compose-hadoop-cluster-mr.yml stop
```

> ⚠️ Always use `stop`. Using `down` or `docker rm` destroys the containers and **permanently deletes all HDFS data**.

---

## 📋 Modules — full reference

> All commands in Hadoop mode use the prefix `hdfs:///` on every input path. This is required by mrjob to resolve paths against HDFS rather than the container's local filesystem.

---

### Module 1 — Weekly price summary

Given any reference date, computes the opening price, closing price, weekly high and weekly low for every stock in the dataset during the natural week (Monday–Sunday) containing that date.

**Parameters:**

| Parameter | Description |
|---|---|
| `--fecha-referencia` | Any date within the target week (`YYYY-MM-DD`) |

**Local:**
```bash
python3 src/ej1_semanal.py \
    --fecha-referencia 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej1_output

python3 ej1_semanal.py -r hadoop \
    --fecha-referencia 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej1_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej1_output/part-*
```

**Sample output:**
```
"BBVA"       "Valor inicial: 18.10, Valor final: 18.10, Valor maximo: 18.26, Valor minimo: 17.72"
"ACS"        "Valor inicial: 105.80, Valor final: 105.80, Valor maximo: 106.90, Valor minimo: 103.20"
"Inditex"    "Valor inicial: 51.46, Valor final: 51.46, Valor maximo: 51.98, Valor minimo: 51.14"
```

---

### Module 2 — Monthly price summary

Same computation as Module 1, extended to the full calendar month containing the reference date.

**Parameters:**

| Parameter | Description |
|---|---|
| `--fecha-referencia` | Any date within the target month (`YYYY-MM-DD`) |

**Local:**
```bash
python3 src/ej2_mensual.py \
    --fecha-referencia 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej2_output

python3 ej2_mensual.py -r hadoop \
    --fecha-referencia 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej2_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej2_output/part-*
```

**Sample output:**
```
"BBVA"    "Valor inicial: 18.99, Valor final: 18.10, Valor maximo: 19.38, Valor minimo: 17.58"
"Repsol"  "Valor inicial: 20.08, Valor final: 23.32, Valor maximo: 24.30, Valor minimo: 19.20"
```

---

### Module 3 — Custom date-range analysis

For a given stock and date range, returns the historical minimum and maximum price and computes the maximum percentage gain and maximum percentage drawdown from the opening price of the period.

**Parameters:**

| Parameter | Description |
|---|---|
| `--accion` | Company name as it appears in the dataset |
| `--fecha-inicio` | Start date of the range (`YYYY-MM-DD`) |
| `--fecha-fin` | End date of the range (`YYYY-MM-DD`) |

**Local:**
```bash
python3 src/ej3_rango.py \
    --accion Bankinter \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
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

**Sample output:**
```
"Bankinter"  "Valor minimo: 7.43, Valor maximo: 14.99, Decremento: 24.26%, Incremento: 52.80%"
```

---

### Module 4 — Min/Max by period

For a given stock and reference date, returns the minimum and maximum price across three lookback windows: the exact day, the trailing 7 days, and the trailing 30 days.

**Parameters:**

| Parameter | Description |
|---|---|
| `--accion` | Company name |
| `--fecha` | Reference date (`YYYY-MM-DD`) |

**Local:**
```bash
python3 src/ej4_minmax.py \
    --accion Bankinter \
    --fecha 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej4_output

python3 ej4_minmax.py -r hadoop \
    --accion Bankinter \
    --fecha 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej4_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej4_output/part-*
```

**Sample output:**
```
"Bankinter"  {
  "ultima_hora":   {"min": null,  "max": null},
  "ultima_semana": {"min": 12.85, "max": 13.85},
  "ultimo_mes":    {"min": 12.67, "max": 14.81}
}
```

---

### Module 5 — Top 5 best-performing stocks

Identifies the five stocks with the highest percentage gain over the trailing week and the trailing month relative to the reference date. Implemented as a **two-step chained MapReduce job**.

**Parameters:**

| Parameter | Description |
|---|---|
| `--fecha` | Reference date representing "today" (`YYYY-MM-DD`) |

**Local:**
```bash
python3 src/ej5_top5_subida.py \
    --fecha 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej5_output

python3 ej5_top5_subida.py -r hadoop \
    --fecha 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej5_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej5_output/part-*
```

**Sample output:**
```
"mes"     ["Repsol: 35.98%", "Indra: 15.62%", "Solaria: 13.19%", "Acciona: 10.77%", "Endesa: 10.27%"]
"semana"  ["Repsol: 4.71%", "Solaria: 4.53%", "Naturgy: 2.15%", "Merlin: 2.13%", "Redeia: 1.82%"]
```

---

### Module 6 — Top 5 worst-performing stocks

Mirror of Module 5 ranked by the largest percentage decline over the trailing week and month. Implemented as a **two-step chained MapReduce job**.

**Parameters:**

| Parameter | Description |
|---|---|
| `--fecha` | Reference date representing "today" (`YYYY-MM-DD`) |

**Local:**
```bash
python3 src/ej6_top5_bajada.py \
    --fecha 2026-03-17 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ej6_output

python3 ej6_top5_bajada.py -r hadoop \
    --fecha 2026-03-17 \
    --output-dir /user/luser/proyecto_final/resultados/ej6_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/ej6_output/part-*
```

**Sample output:**
```
"mes"     ["IAG: 19.65%", "Grifols: 17.32%", "Almirall: 16.33%", "ArcelorMittal: 16.29%", "Aena: 10.79%"]
"semana"  ["ArcelorMittal: 3.94%", "Amadeus: 2.98%", "IAG: 2.39%", "Inditex: 2.13%", "Acerinox: 1.65%"]
```

---

### Module 7 — Stocks above a growth threshold

Given a minimum percentage and a date range, returns all stocks whose price appreciated by at least that amount during the period, sorted from lowest to highest growth. Implemented as a **two-step chained MapReduce job**.

**Parameters:**

| Parameter | Description |
|---|---|
| `--fecha-inicio` | Start date of the period (`YYYY-MM-DD`) |
| `--fecha-fin` | End date of the period (`YYYY-MM-DD`) |
| `--porcentaje` | Minimum growth threshold (e.g. `20` for ≥ 20%) |

**Local:**
```bash
python3 src/ej7_incremento.py \
    --fecha-inicio 2025-03-17 \
    --fecha-fin 2026-03-17 \
    --porcentaje 20 \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
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

**Sample output** (≥ 20% threshold, full-year period):
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
*20 out of 30 IBEX 35 companies exceeded the 20% growth threshold over the analysed period.*

---

## 🔬 Advanced modules — multi-dataset joins

These three modules perform a **distributed join** between the daily price dataset and the fundamentals dataset, using the company name as the join key. The Mapper identifies the source of each record by inspecting the column structure (date-formatted fields indicate price data; sector/ratio fields indicate fundamentals) and tags records with `HIST` or `FUND` accordingly. The Reducer then merges both sources per company to compute cross-dataset metrics.

---

### Advanced module 1 — Annual volatility vs P/E ratio

Computes each company's annual price volatility — defined as the percentage spread between the yearly high and yearly low — and cross-references it with the P/E ratio. This allows assessment of whether higher-valued stocks (high P/E) tend to carry proportionally higher price risk.

**Local:**
```bash
python3 src/avanzado1_volatilidad_per.py \
    data/raw/ibex35_fundamentales_2026-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/av1_output

python3 avanzado1_volatilidad_per.py -r hadoop \
    --output-dir /user/luser/proyecto_final/resultados/av1_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2026-03-17.csv \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/av1_output/part-*
```

**Sample output:**
```
"IAG"      ["Sector: Industrials",       "PER: 5.87",   "Volatilidad: 104.69%"]
"Naturgy"  ["Sector: Utilities",         "PER: 11.83",  "Volatilidad: 22.29%"]
"Solaria"  ["Sector: Utilities",         "PER: 19.73",  "Volatilidad: 255.50%"]
"Inditex"  ["Sector: Consumer Cyclical", "PER: 26.97",  "Volatilidad: 43.26%"]
```

**Key insight:** The P/E ratio is an incomplete valuation metric without volatility context. IAG carries a P/E of 5.9 — theoretically cheap — yet posts a 104% annual volatility, rendering any earnings-recovery timeline unreliable. Naturgy at P/E 11.8 with only 22% volatility offers a substantially more defensible valuation.

---

### Advanced module 2 — ROE vs annual price return

Cross-references each company's Return on Equity (ROE) — sourced from the prior-year fundamentals dataset to reflect the information available to the market at the start of the period — against the actual share price appreciation recorded over the following 12 months.

**Local:**
```bash
python3 src/avanzado2_roe_rendimiento.py \
    data/raw/ibex35_fundamentales_2025-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/av2_output

python3 avanzado2_roe_rendimiento.py -r hadoop \
    --output-dir /user/luser/proyecto_final/resultados/av2_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2025-03-17.csv \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/av2_output/part-*
```

**Sample output:**
```
"Indra"      ["ROE: 25.13%", "Revalorizacion: 132.00%"]
"Repsol"     ["ROE: 7.55%",  "Revalorizacion: 110.85%"]
"Inditex"    ["ROE: 29.81%", "Revalorizacion: 17.95%"]
"Telefonica" ["ROE: -0.25%", "Revalorizacion: -12.10%"]
```

**Key insight:** High ROE does not reliably predict near-term price appreciation because operational efficiency is already priced into the stock. Inditex (ROE 29.8%) appreciated only 18% as its quality was fully reflected in the market price. Repsol (ROE 7.6%) surged 111% driven by external commodity factors — demonstrating that short-term returns are primarily driven by surprise, not internal efficiency.

---

### Advanced module 3 — Average return by sector

Calculates the mean annual price appreciation for each economic sector represented in the IBEX 35. Implemented as a **two-step chained MapReduce job**: the first job joins both datasets and computes per-company returns; the second job groups by sector and aggregates the arithmetic mean.

**Local:**
```bash
python3 src/avanzado3_influencia_sector.py \
    data/raw/ibex35_fundamentales_2026-03-17.csv \
    data/raw/ibex35_2026-03-17.csv
```

**Hadoop:**
```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/av3_output

python3 avanzado3_influencia_sector.py -r hadoop \
    --output-dir /user/luser/proyecto_final/resultados/av3_output \
    hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2026-03-17.csv \
    hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv

hdfs dfs -cat /user/luser/proyecto_final/resultados/av3_output/part-*
```

**Sample output:**
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

**Key insight:** Sector allocation accounts for a substantial portion of portfolio returns. Energy and Technology led the IBEX 35 with mean appreciations above 50%, while Communication Services — represented solely by Telefónica — was the only sector to post a negative return over the period.

---

## 💾 Persisting results

### Option A — Master script (all modules in sequence)

```bash
# Inside the container as luser, with venv_hadoop active
bash /home/luser/ejecutar_todo_hadoop.sh
```

Each output is written to `/home/luser/resultados_proyecto/<module>_resultado.txt`.

### Option B — Manual collection

```bash
mkdir -p /home/luser/resultados_proyecto

for module in ej1 ej2 ej3 ej4 ej5 ej6 ej7 av1 av2 av3; do
    hdfs dfs -cat /user/luser/proyecto_final/resultados/${module}_output/part-* \
        > /home/luser/resultados_proyecto/${module}_resultado.txt 2>/dev/null
    echo "saved: ${module}"
done
```

### Export to the host machine

From the host terminal:

```bash
docker cp namenode-mr:/home/luser/resultados_proyecto/ ./resultados/
```

The `./resultados/` directory on the host is a permanent copy independent of the Docker lifecycle.

---

## 🔧 Troubleshooting

### `OSError: Input path does not exist`

mrjob requires the `hdfs:///` prefix on all HDFS input paths when running with `-r hadoop`. Without it, mrjob looks for the file on the container's local filesystem.

```bash
# Incorrect
python3 module.py -r hadoop /user/luser/proyecto_final/data/ibex35.csv

# Correct
python3 module.py -r hadoop hdfs:///user/luser/proyecto_final/data/ibex35.csv
```

Verify that the file exists in HDFS:

```bash
hdfs dfs -ls /user/luser/proyecto_final/data/
```

### `Output directory already exists`

HDFS does not overwrite existing output directories. Remove the previous output before re-running:

```bash
hdfs dfs -rm -r /user/luser/proyecto_final/resultados/ejX_output
```

### `ModuleNotFoundError: No module named 'mrjob'`

The virtual environment is not active:

```bash
source ~/venv_hadoop/bin/activate
```

### `python3: can't open file '/home/luser/module.py'`

The script has not been copied into the container:

```bash
docker cp src/module.py namenode-mr:/home/luser/
```

### Job hangs or does not complete

Inspect running applications via the YARN web interface at http://localhost:8088 or from the command line:

```bash
# List active applications
yarn application -list

# Terminate a stuck application
yarn application -kill <application_id>
```

### Container runs out of memory

Check container resource usage:

```bash
docker stats --no-stream
```

If containers are being killed due to memory pressure, reduce the memory limits in `compose-hadoop-cluster-mr.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 2048m
```

---

## 👤 Author

**Denys Litvynov Lymanets**

---

<div align="center">

*Built with Apache Hadoop · mrjob · Yahoo Finance*

</div>
