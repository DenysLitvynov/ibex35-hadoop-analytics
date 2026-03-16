import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# Diccionario de empresas del IBEX 35
empresas = {
    "ANA.MC":"Acciona",
    "ACX.MC":"Acerinox",
    "ACS.MC":"ACS",
    "AENA.MC":"Aena",
    "AMS.MC":"Amadeus",
    "BBVA.MC":"BBVA",
    "CABK.MC":"CaixaBank",
    "CLNX.MC":"Cellnex",
    "COL.MC":"Colonial",
    "ELE.MC":"Endesa",
    "ENG.MC":"Enagás",
    "FER.MC":"Ferrovial",
    "GRF.MC":"Grifols",
    "IAG.MC":"IAG",
    "IBE.MC":"Iberdrola",
    "IDR.MC":"Indra",
    "ITX.MC":"Inditex",
    "LOG.MC":"Logista",
    "MAP.MC":"Mapfre",
    "MEL.MC":"Meliá",
    "MRL.MC":"Merlin",
    "NTGY.MC":"Naturgy",
    "RED.MC":"Redeia",
    "REP.MC":"Repsol",
    "SAB.MC":"Sabadell",
    "SAN.MC":"Santander",
    "SCYR.MC":"Sacyr",
    "SLR.MC":"Solaria",
    "TEF.MC":"Telefónica",
    "UNI.MC":"Unicaja"
}

# Rango de fechas dinámico: desde hoy hace un año hasta hoy (inclusive)
hoy = date.today()
inicio = (hoy - timedelta(days=365)).strftime("%Y-%m-%d")
fin = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")  # yfinance usa rango [start, end), +1 para incluir hoy

print(f"Período de descarga: {inicio} → {hoy}")
print("-" * 30)

filas = []

for ticker, nombre in empresas.items():

    print(f"Descargando {nombre} ({ticker})...")

    # Descarga de datos
    df = yf.download(ticker, start=inicio, end=fin, progress=False)

    if df.empty:
        print(f"Advertencia: No hay datos para {nombre}")
        continue

    # SOLUCIÓN AL ERROR: Aplanar el MultiIndex de las columnas
    # yfinance devuelve niveles [Métrica, Ticker]. Nos quedamos solo con la Métrica.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Calcular variaciones
    df["var"] = df["Close"].diff()
    df["var_pct"] = df["Close"].pct_change() * 100

    # Reemplazar NaN del primer día con ceros
    df["var"] = df["var"].fillna(0)
    df["var_pct"] = df["var_pct"].fillna(0)

    # Iterar por cada día de cotización
    for fecha, row in df.iterrows():
        filas.append({
            "empresa": nombre,
            "fecha": fecha.date(),
            # Convertimos a float/int nativo de Python para evitar errores de Series
            "ultimo": round(float(row["Close"]), 2),
            "var": round(float(row["var"]), 2),
            "var_pct": round(float(row["var_pct"]), 2),
            "maximo": round(float(row["High"]), 2),
            "minimo": round(float(row["Low"]), 2),
            "volumen": int(row["Volume"])
        })

# Crear el DataFrame final
dataset = pd.DataFrame(filas)

# Ordenar por fecha (ascendente) y empresa (alfabético)
dataset = dataset.sort_values(["fecha", "empresa"])

# Guardar en data/raw relativo a la raíz del proyecto
# El script está en src/scraper/, subimos dos niveles para llegar a la raíz
output_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

nombre_fichero = f"ibex35_{hoy.strftime('%Y-%m-%d')}.csv"
output_path = output_dir / nombre_fichero
dataset.to_csv(output_path, index=False)

print("-" * 30)
print("Proceso finalizado con éxito.")
print(f"Dataset creado: {output_path}")
print(f"Total registros: {len(dataset)}")
