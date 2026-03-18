import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
import random

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

# Fecha específica solicitada
fecha_objetivo = "2025-03-17"
filas = []

print(f"Iniciando extracción histórica para {fecha_objetivo}...")

for ticker, nombre in empresas.items():
    print(f"Métricas {nombre} (Histórico)...")
    try:
        # 1. Anti-bloqueo: Espera aleatoria
        time.sleep(random.uniform(2, 4))
        
        stock = yf.Ticker(ticker)
        
        # 2. Precio histórico para calcular el PER
        hist = stock.history(start="2025-03-17", end="2025-03-24")
        precio = hist.iloc[0]['Close'] if not hist.empty else 0.0
        
        # 3. Obtener estados financieros (Balance, Cuenta Resultados, etc.)
        # Buscamos la columna más cercana a marzo 2025 (normalmente el cierre de 2024)
        inc = stock.income_stmt
        bal = stock.balance_sheet
        
        # Extraemos valores con seguridad (.get o try/except)
        def get_val(df, label):
            try: return df.loc[label].iloc[0]
            except: return 0.0

        eps = get_val(inc, 'Basic EPS')
        net_income = get_val(inc, 'Net Income')
        equity = get_val(bal, 'Stockholders Equity')
        debt = get_val(bal, 'Total Debt')
        ebitda = get_val(inc, 'EBITDA')
        
        # Calculamos ratios (Mismas columnas que tu original)
        filas.append({
            "empresa": nombre,
            "sector": stock.info.get("sector", "N/A"),
            "per": precio / eps if eps > 0 else 0.0,
            "roe": net_income / equity if equity > 0 else 0.0,
            "deuda_equity": (debt / equity) * 100 if equity > 0 else 0.0, # Suele ser %
            "dividend_yield": stock.info.get("dividendYield", 0.0), # Difícil de sacar histórico exacto, usamos info
            "market_cap": stock.info.get("marketCap", 0.0), # Referencia actual o aproximada
            "ebitda": ebitda
        })
        print(f"  [OK] Procesado.")

    except Exception as e:
        print(f"  [!] Fallo en {nombre}: {e}")
        filas.append({
            "empresa": nombre, "sector": "N/A", "per": 0.0, "roe": 0.0, 
            "deuda_equity": 0.0, "dividend_yield": 0.0, "market_cap": 0.0, "ebitda": 0.0
        })

# --- Guardado respetando tu estructura ---
dataset = pd.DataFrame(filas)
output_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

# Nombre de archivo con la fecha que querías
dataset.to_csv(output_dir / f"ibex35_fundamentales_{fecha_objetivo}.csv", index=False)
print(f"\nHecho. Archivo guardado en data/raw como ibex35_fundamentales_{fecha_objetivo}.csv")