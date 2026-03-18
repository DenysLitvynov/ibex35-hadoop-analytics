````markdown
# 📈 IBEX35 Big Data Analytics (Hadoop + MapReduce)

Proyecto de análisis de cotizaciones del **IBEX 35** usando **MapReduce** sobre un clúster **Hadoop** (Docker).  
Incluye desde análisis básicos hasta estudios avanzados de correlación financiera.

---

## 🛠️ 1. Pruebas en Local (Quick Start)

Antes de usar Hadoop, valida los scripts en local.

### Requisitos
- Python 3.x
- Librería:
```bash
pip install mrjob
````

### Ejecución

```bash
python scripts/ejercicio_X.py datos/archivo.csv
```

**Ejemplo:**

```bash
python ej1_semanal.py --fecha-referencia 2026-03-17 data/ibex35_2026-03-17.csv
```

---

## 🚀 2. Despliegue en Hadoop

### ▶️ A. Levantar clúster

```bash
hadoop-up
```

---

### 📂 B. Preparar HDFS

Entrar al contenedor:

```bash
docker exec -it namenode-mr /bin/bash
```

Subir datos:

```bash
hdfs dfs -mkdir -p /user/luser/proyecto/data
hdfs dfs -put /ruta/local/tus_datos.csv /user/luser/proyecto/data/
```

---

### ⚙️ C. Ejecutar todo

```bash
bash ejecutar_todo_hadoop.sh
```

---

### 📥 D. Recuperar resultados

**1. HDFS → Contenedor**

```bash
hdfs dfs -get /user/luser/proyecto/resultados/ej_output/part-* ./resultado_ej.txt
```

**2. Contenedor → Local**

```bash
docker cp namenode-mr:/home/luser/resultado_ej.txt ./mis_resultados/
```

---

## 📊 Ejercicios

| Nivel      | Descripción              |
| ---------- | ------------------------ |
| Básico     | Listados, rangos y Top 5 |
| Avanzado 1 | Volatilidad vs PER       |
| Avanzado 2 | ROE vs Rendimiento       |
| Avanzado 3 | Análisis sectorial       |

---

## 🛑 Apagado seguro

```bash
hadoop-down
```

⚠️ No uses `down` directamente para evitar pérdida de datos.

---

