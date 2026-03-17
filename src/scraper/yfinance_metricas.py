import yfinance as yf
import pandas as pd
from datetime import date
from pathlib import Path

empresas = {
    "ANA.MC": "Acciona", "ANE.MC": "Acciona Energía", "ACX.MC": "Acerinox", "ACS.MC": "ACS",
    "AENA.MC": "Aena", "ALM.MC": "Almirall", "AMS.MC": "Amadeus", "MTS.MC": "ArcelorMittal",
    "BKT.MC": "Bankinter", "BBVA.MC": "BBVA", "CABK.MC": "CaixaBank", "CLNX.MC": "Cellnex",
    "COL.MC": "Colonial", "ELE.MC": "Endesa", "ENG.MC": "Enagás", "FER.MC": "Ferrovial",
    "GRF.MC": "Grifols", "IAG.MC": "IAG", "IBE.MC": "Iberdrola", "IDR.MC": "Indra",
    "ITX.MC": "Inditex", "LOG.MC": "Logista", "MAP.MC": "Mapfre", "MEL.MC": "Meliá",
    "MRL.MC": "Merlin", "NTGY.MC": "Naturgy", "PUIG.MC": "Puig", "RED.MC": "Redeia",
    "REP.MC": "Repsol", "SAB.MC": "Sabadell", "SAN.MC": "Santander", "SCYR.MC": "Sacyr",
    "SLR.MC": "Solaria", "TEF.MC": "Telefónica", "UNI.MC": "Unicaja"
}

hoy = date.today().isoformat()
filas = []

for ticker, nombre in empresas.items():
    print(f"Métricas {nombre}...")
    try:
        stock = yf.Ticker(ticker)
        # Usamos .get() con 0.0 por defecto para que nunca sea None
        inf = stock.info
        filas.append({
            "empresa": nombre,
            "sector": inf.get("sector", "N/A"),
            "per": inf.get("trailingPE", 0.0),
            "roe": inf.get("returnOnEquity", 0.0),
            "deuda_equity": inf.get("debtToEquity", 0.0),
            "dividend_yield": inf.get("dividendYield", 0.0),
            "market_cap": inf.get("marketCap", 0.0),
            "ebitda": inf.get("ebitda", 0.0)
        })
    except:
        filas.append({
            "empresa": nombre, "sector": "N/A", "per": 0.0, "roe": 0.0, 
            "deuda_equity": 0.0, "dividend_yield": 0.0, "market_cap": 0.0, "ebitda": 0.0
        })

dataset = pd.DataFrame(filas)
output_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)
dataset.to_csv(output_dir / f"ibex35_fundamentales_{hoy}.csv", index=False)
print("Hecho.")
