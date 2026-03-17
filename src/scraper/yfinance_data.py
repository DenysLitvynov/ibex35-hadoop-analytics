import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# Lista completa y ordenada de las 35 empresas
empresas = {
    "ANA.MC": "Acciona", "ANE.MC": "Acciona Energia", "ACX.MC": "Acerinox", "ACS.MC": "ACS",
    "AENA.MC": "Aena", "ALM.MC": "Almirall", "AMS.MC": "Amadeus", "MTS.MC": "ArcelorMittal",
    "BKT.MC": "Bankinter", "BBVA.MC": "BBVA", "CABK.MC": "CaixaBank", "CLNX.MC": "Cellnex",
    "COL.MC": "Colonial", "ELE.MC": "Endesa", "ENG.MC": "Enagas", "FER.MC": "Ferrovial",
    "GRF.MC": "Grifols", "IAG.MC": "IAG", "IBE.MC": "Iberdrola", "IDR.MC": "Indra",
    "ITX.MC": "Inditex", "LOG.MC": "Logista", "MAP.MC": "Mapfre", "MEL.MC": "Melia",
    "MRL.MC": "Merlin", "NTGY.MC": "Naturgy", "PUIG.MC": "Puig", "RED.MC": "Redeia",
    "REP.MC": "Repsol", "SAB.MC": "Sabadell", "SAN.MC": "Santander", "SCYR.MC": "Sacyr",
    "SLR.MC": "Solaria", "TEF.MC": "Telefonica", "UNI.MC": "Unicaja"
}

fin = date.today()
inicio = fin - timedelta(days=365)
filas = []

print(f"Descargando datos: {inicio} a {fin}")

for ticker, nombre in empresas.items():
    print(f"Descargando {nombre}...")
    try:
        # Descargamos los datos
        df = yf.download(ticker, start=inicio, end=fin, progress=False)
        
        if df.empty or len(df) < 2:
            continue

        # Forzamos a que no haya MultiIndex en las columnas (el error de las Series)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Calculamos variaciones como en tu archivo original
        df["var"] = df["Close"].diff().fillna(0)
        df["var_pct"] = df["Close"].pct_change().fillna(0) * 100

        for fecha, row in df.iterrows():
            filas.append({
                "empresa": nombre,
                "fecha": fecha.date().isoformat(),
                "ultimo": round(float(row["Close"]), 2),
                "var": round(float(row["var"]), 2),
                "var_pct": round(float(row["var_pct"]), 2),
                "maximo": round(float(row["High"]), 2),
                "minimo": round(float(row["Low"]), 2),
                "volumen": int(row["Volume"])
            })
    except Exception as e:
        print(f"Saltando {nombre} por error: {e}")
        continue

if not filas:
    print("Error crítico: No se ha podido descargar ningún dato.")
else:
    dataset = pd.DataFrame(filas)
    dataset = dataset.sort_values(["empresa", "fecha"])
    
    output_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    fichero = output_dir / f"ibex35_{fin}.csv"
    dataset.to_csv(fichero, index=False)
    print(f"Guardado en: {fichero}")
