#!/bin/bash
# ============================================================
#  SCRIPT MAESTRO — Proyecto Big Data IBEX35
#  Ejecuta los 10 ejercicios en Hadoop y guarda los resultados
#  Autor: Denys Litvynov Lymanets
#  Uso:  bash ejecutar_todo_hadoop.sh
# ============================================================

# ── Colores para mensajes ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Configuración ──────────────────────────────────────────
HDFS_BASE="/user/luser/proyecto_final"
HDFS_RESULTADOS="$HDFS_BASE/resultados"
LOCAL_RESULTADOS="/home/luser/resultados_proyecto"
SCRIPTS_DIR="/home/luser"
VENV="$HOME/venv_hadoop"

# ── RUTAS HDFS con prefijo hdfs:/// (OBLIGATORIO para mrjob -r hadoop) ──
CSV_COTIZ="hdfs:///user/luser/proyecto_final/data/ibex35_2026-03-17.csv"
CSV_FUND_2026="hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2026-03-17.csv"
CSV_FUND_2025="hdfs:///user/luser/proyecto_final/data/ibex35_fundamentales_2025-03-17.csv"

# Parámetros de fecha
FECHA_HOY="2026-03-17"
FECHA_INICIO_ANIO="2025-03-17"

# ── Activar venv ───────────────────────────────────────────
echo -e "${BLUE}[0] Activando entorno virtual Python...${NC}"
source "$VENV/bin/activate" || { echo -e "${RED}ERROR: No se encontró el venv en $VENV${NC}"; exit 1; }
echo -e "${GREEN}    venv activo: $(which python3)${NC}"

# ── Crear directorios de resultados ───────────────────────
echo -e "${BLUE}[INIT] Creando directorios...${NC}"
mkdir -p "$LOCAL_RESULTADOS"
hdfs dfs -mkdir -p "$HDFS_RESULTADOS"
echo -e "${GREEN}    Directorios OK${NC}"

# ── Verificar que los CSVs están en HDFS ──────────────────
echo -e "${BLUE}[CHECK] Verificando ficheros en HDFS...${NC}"
for csv in "$CSV_COTIZ" "$CSV_FUND_2026" "$CSV_FUND_2025"; do
    ruta_local="${csv#hdfs://}"
    if hdfs dfs -test -e "$ruta_local" 2>/dev/null; then
        echo -e "${GREEN}    ✓ $ruta_local${NC}"
    else
        echo -e "${RED}    ✗ NO ENCONTRADO: $ruta_local${NC}"
        echo -e "${RED}      Sube con: hdfs dfs -put /tmp/<fichero> /user/luser/proyecto_final/data/${NC}"
    fi
done

# ── Función auxiliar: ejecutar y guardar ──────────────────
run_job() {
    local NUM=$1
    local NOMBRE=$2
    local SCRIPT=$3
    # Todos los argumentos extra (flags + rutas hdfs:///) están en $4 en adelante
    shift 3
    local ARGS="$@"

    local OUTPUT_HDFS="$HDFS_RESULTADOS/ej${NUM}_output"
    local OUTPUT_LOCAL="$LOCAL_RESULTADOS/ej${NUM}_${NOMBRE}.txt"

    echo ""
    echo -e "${YELLOW}══════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  EJERCICIO $NUM — $NOMBRE${NC}"
    echo -e "${YELLOW}══════════════════════════════════════════════${NC}"

    # Borrar output previo en HDFS si existe
    hdfs dfs -test -d "$OUTPUT_HDFS" && hdfs dfs -rm -r "$OUTPUT_HDFS"

    # Ejecutar el job en Hadoop
    echo -e "${BLUE}  Ejecutando: python3 $SCRIPT -r hadoop --output-dir $OUTPUT_HDFS $ARGS${NC}"
    python3 "$SCRIPTS_DIR/$SCRIPT" -r hadoop \
        --output-dir "$OUTPUT_HDFS" \
        $ARGS

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ Job completado correctamente${NC}"

        # Guardar resultado en fichero local
        {
            echo "=== EJERCICIO $NUM — $NOMBRE ==="
            echo "Comando: python3 $SCRIPT -r hadoop $ARGS"
            echo "Fecha ejecucion: $(date)"
            echo "---"
            hdfs dfs -cat "$OUTPUT_HDFS/part-*" 2>/dev/null
        } > "$OUTPUT_LOCAL"

        echo -e "${GREEN}  ✓ Resultado local:  $OUTPUT_LOCAL${NC}"
        echo -e "${GREEN}  ✓ Resultado HDFS:   $OUTPUT_HDFS${NC}"
    else
        echo -e "${RED}  ✗ ERROR en el ejercicio $NUM${NC}"
    fi
}

# ══════════════════════════════════════════════════════════
#  EJERCICIOS OBLIGATORIOS
# ══════════════════════════════════════════════════════════

run_job 1 "semanal" "ej1_semanal.py" \
    --fecha-referencia "$FECHA_HOY" \
    "$CSV_COTIZ"

run_job 2 "mensual" "ej2_mensual.py" \
    --fecha-referencia "$FECHA_HOY" \
    "$CSV_COTIZ"

run_job 3 "rango_bankinter" "ej3_rango.py" \
    --accion Bankinter \
    --fecha-inicio "$FECHA_INICIO_ANIO" \
    --fecha-fin "$FECHA_HOY" \
    "$CSV_COTIZ"

run_job 4 "minmax_bankinter" "ej4_minmax.py" \
    --accion Bankinter \
    --fecha "$FECHA_HOY" \
    "$CSV_COTIZ"

run_job 5 "top5_subida" "ej5_top5_subida.py" \
    --fecha "$FECHA_HOY" \
    "$CSV_COTIZ"

run_job 6 "top5_bajada" "ej6_top5_bajada.py" \
    --fecha "$FECHA_HOY" \
    "$CSV_COTIZ"

run_job 7 "incremento_pct20" "ej7_incremento.py" \
    --fecha-inicio "$FECHA_INICIO_ANIO" \
    --fecha-fin "$FECHA_HOY" \
    --porcentaje 20 \
    "$CSV_COTIZ"

# ══════════════════════════════════════════════════════════
#  EJERCICIOS AVANZADOS
# ══════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}══ AVANZADOS (join de dos ficheros CSV) ══${NC}"

run_job "av1" "volatilidad_per" "avanzado1_volatilidad_per.py" \
    "$CSV_FUND_2026" \
    "$CSV_COTIZ"

run_job "av2" "roe_rendimiento" "avanzado2_roe_rendimiento.py" \
    "$CSV_FUND_2025" \
    "$CSV_COTIZ"

# NOMBRE ACTUALIZADO: avanzado3_influencia_sector.py
run_job "av3" "influencia_sector" "avanzado3_influencia_sector.py" \
    "$CSV_FUND_2026" \
    "$CSV_COTIZ"

# ══════════════════════════════════════════════════════════
#  RESUMEN FINAL
# ══════════════════════════════════════════════════════════
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  TODOS LOS JOBS COMPLETADOS${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "Resultados locales en:  ${YELLOW}$LOCAL_RESULTADOS/${NC}"
echo -e "Resultados en HDFS en:  ${YELLOW}$HDFS_RESULTADOS/${NC}"
echo ""
echo "Ficheros generados:"
ls -lh "$LOCAL_RESULTADOS/"
