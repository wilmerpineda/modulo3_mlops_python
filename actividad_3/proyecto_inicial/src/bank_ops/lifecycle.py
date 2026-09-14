"""Registro local de un operador; reiniciar API después de promover o revertir."""
import json, os
from datetime import datetime, timezone
from .config import ARTIFACTS, FEATURES
from .model import read_model, metrics
from .data import load, partitions

def pointer():
    return json.loads((ARTIFACTS/"current.json").read_text(encoding="utf-8"))

def compare(candidate, incumbent):
    _,val,_=partitions(load())
    reports={}
    for version in [candidate,incumbent]:
        model,meta=read_model(version)
        reports[version]=metrics((val.y=="yes").astype(int),model.predict_proba(val[FEATURES])[:,1],meta["threshold"])
    c,i=reports[candidate],reports[incumbent]
    # TODO A3-01: aplicar AP -0.005, recall -0.02 y Brier +0.01.
    # Devolver candidate, incumbent, checks, eligible, validation y policy.
    # eligible exige todas las condiciones y AP definida en ambos modelos.
    raise NotImplementedError("A3-01: completar política de comparación")


def set_current(version, actor, reason, action, previous=None):
    if not actor.strip() or not reason.strip(): raise ValueError("Responsable y justificación obligatorios")
    _,meta=read_model(version)
    entry={"version":version,"previous":previous,"actor":actor,"reason":reason,"action":action,"utc":datetime.now(timezone.utc).isoformat(),"model_sha256":meta["model_sha256"]}
    ARTIFACTS.mkdir(parents=True,exist_ok=True)
    temp=ARTIFACTS/"current.tmp"; temp.write_text(json.dumps(entry,indent=2),encoding="utf-8"); os.replace(temp,ARTIFACTS/"current.json")
    with (ARTIFACTS/"audit.jsonl").open("a",encoding="utf-8") as f: f.write(json.dumps(entry)+"\n")
    return entry

def promote(version, actor, reason):
    current=pointer()["version"] if (ARTIFACTS/"current.json").exists() else None
    if current==version: raise ValueError("La versión ya está activa")
    if current and not compare(version,current)["eligible"]: raise ValueError("Candidato rechazado por política de validación")
    return set_current(version,actor,reason,"promote",current)

def rollback(actor,reason):
    current=pointer()
    if not current.get("previous"): raise ValueError("No hay versión anterior")
    return set_current(current["previous"],actor,reason,"rollback",current["version"])
