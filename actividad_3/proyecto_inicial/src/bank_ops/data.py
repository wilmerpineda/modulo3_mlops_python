"""Snapshot verificable. Nunca descarga durante pruebas ni inferencia."""
import argparse, hashlib, json, zipfile, io, urllib.request
import pandas as pd
from .config import DATA, FEATURES
URL = "https://archive.ics.uci.edu/static/public/222/bank%2Bmarketing.zip"

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def download():
    DATA.mkdir(parents=True, exist_ok=True)
    payload = urllib.request.urlopen(URL, timeout=60).read()
    outer = zipfile.ZipFile(io.BytesIO(payload))
    inner = zipfile.ZipFile(io.BytesIO(outer.read("bank.zip"))) if "bank.zip" in outer.namelist() else outer
    raw = inner.read("bank-full.csv")
    (DATA / "bank-full.csv").write_bytes(raw)
    meta = {"source": URL, "dataset": "UCI Bank Marketing, bank-full.csv", "doi": "10.24432/C5K306", "license": "CC BY 4.0", "sha256": digest(DATA / "bank-full.csv"), "rows": 45211, "synthetic": False}
    (DATA / "provenance.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

def validate(df, target=True):
    required = FEATURES + ["age"] + (["y"] if target else [])
    missing = sorted(set(required) - set(df.columns))
    if missing: raise ValueError(f"Columnas ausentes: {missing}")
    if df.empty: raise ValueError("Lote vacío")
    if df[required].isna().any().any(): raise ValueError("Nulos no permitidos")
    for col in ["balance", "campaign", "pdays", "previous", "age"]:
        if not pd.api.types.is_numeric_dtype(df[col]): raise ValueError(f"Tipo inválido: {col}")
    if not df.age.between(18, 100).all(): raise ValueError("Edad fuera del contrato")
    if not df.campaign.between(1,100).all(): raise ValueError("campaign fuera del contrato")
    if (df.previous < 0).any() or (df.pdays < -1).any(): raise ValueError("Historial inválido")
    if target and not df.y.isin(["yes", "no"]).all(): raise ValueError("Target inválido")

def load():
    path = DATA / "bank-full.csv"
    meta = json.loads((DATA / "provenance.json").read_text(encoding="utf-8"))
    if digest(path) != meta["sha256"]: raise ValueError("Checksum del snapshot incorrecto")
    df = pd.read_csv(path, sep=";")
    validate(df)
    if len(df) != meta["rows"]: raise ValueError("Cantidad de filas inesperada")
    df["row_id"] = range(len(df))
    return df

def partitions(df):
    # Orden original; no reconstruir fechas que el archivo no contiene.
    n=len(df); a=int(n*.6); b=int(n*.8)
    return df.iloc[:a].copy(), df.iloc[a:b].copy(), df.iloc[b:].copy()

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--download", action="store_true"); args=p.parse_args()
    if args.download: download()
    frame=load(); print({"rows":len(frame), "partitions":[len(x) for x in partitions(frame)], "sha256":digest(DATA/"bank-full.csv")})
