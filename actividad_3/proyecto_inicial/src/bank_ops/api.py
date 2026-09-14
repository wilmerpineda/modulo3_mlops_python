import json, threading, time, uuid
from contextlib import asynccontextmanager
from datetime import datetime,timezone
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, ConfigDict
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from .config import FEATURES, REPORTS
from .model import read_model
from .lifecycle import pointer

class Request(BaseModel):
    model_config=ConfigDict(extra="forbid")
    balance: float = Field(allow_inf_nan=False)
    campaign: int = Field(ge=1,le=100)
    pdays: int = Field(ge=-1)
    previous: int = Field(ge=0)
    job: str = Field(min_length=1,max_length=40)
    marital: str = Field(min_length=1,max_length=20)
    education: str = Field(min_length=1,max_length=30)
    default: str = Field(pattern="^(yes|no)$")
    housing: str = Field(pattern="^(yes|no)$")
    loan: str = Field(pattern="^(yes|no)$")
    contact: str = Field(min_length=1,max_length=20)
    month: str = Field(pattern="^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$")
    poutcome: str = Field(min_length=1,max_length=20)

class Prediction(BaseModel):
    prediction_id: str
    probability: float
    prediction: int
    threshold: float
    model_version: str

def create_app():
    registry=CollectorRegistry()
    requests=Counter("bank_http_requests_total","Solicitudes HTTP",["route","status"],registry=registry)
    latency=Histogram("bank_http_duration_seconds","Latencia HTTP",["route"],registry=registry,buckets=(.005,.01,.025,.05,.1,.25,.5,1,2,5))
    predictions=Counter("bank_predictions_total","Predicciones",["class"],registry=registry)
    ready=Gauge("bank_model_ready","Modelo listo",registry=registry)
    lock=threading.Lock()
    @asynccontextmanager
    async def lifespan(app):
        try: app.state.model,app.state.meta=read_model(pointer()["version"]); ready.set(1)
        except (OSError,ValueError,KeyError): app.state.model=None; app.state.meta=None; ready.set(0)
        yield
    app=FastAPI(title="Bank Ops · laboratorio educativo",lifespan=lifespan)
    @app.middleware("http")
    async def instrument(request,call_next):
        started=time.perf_counter(); status="500"
        try:
            response=await call_next(request); status=str(response.status_code); return response
        finally:
            route=getattr(request.scope.get("route"),"path","unmatched")
            if route!="/metrics": requests.labels(route,status).inc(); latency.labels(route).observe(time.perf_counter()-started)
    @app.get("/health")
    def health(): return {"status":"alive"}
    @app.get("/ready")
    def readiness():
        if app.state.model is None: raise HTTPException(503,"Modelo no disponible")
        return {"status":"ready","model_version":app.state.meta["version"]}
    @app.get("/model/metadata")
    def metadata():
        if app.state.model is None: raise HTTPException(503,"Modelo no disponible")
        return app.state.meta
    @app.get("/metrics")
    def metric_endpoint(): return Response(generate_latest(registry),headers={"Content-Type":CONTENT_TYPE_LATEST})
    @app.post("/predict",response_model=Prediction)
    def predict(payload:Request):
        if app.state.model is None: raise HTTPException(503,"Modelo no disponible")
        prob=float(app.state.model.predict_proba(pd.DataFrame([payload.model_dump()])[FEATURES])[0,1])
        meta=app.state.meta; pred=int(prob>=meta["threshold"])
        result=Prediction(prediction_id=str(uuid.uuid4()),probability=prob,prediction=pred,threshold=meta["threshold"],model_version=meta["version"])
        entry=result.model_dump(); entry["utc"]=datetime.now(timezone.utc).isoformat()
        # Un worker y archivo local para enseñanza. No se guardan atributos personales.
        REPORTS.mkdir(parents=True,exist_ok=True)
        with lock, (REPORTS/"predictions.jsonl").open("a",encoding="utf-8") as stream: stream.write(json.dumps(entry)+"\n")
        predictions.labels(str(pred)).inc(); return result
    return app

app=create_app()
