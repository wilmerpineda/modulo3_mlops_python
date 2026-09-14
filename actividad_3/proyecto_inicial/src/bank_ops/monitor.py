import json
import numpy as np
import pandas as pd
from .config import FEATURES, NUMERIC, CATEGORICAL, REPORTS, SEED
from .data import validate, load, partitions
from .model import read_model, metrics

def scenario(frame, name):
    result=frame.copy()
    if name=="shift":
        result["balance"] = result.balance + 12000
        result["contact"] = "unknown"
    elif name=="invalid": result.loc[result.index[0],"campaign"]=-3
    elif name=="degraded":
        # Intervención artificial en etiquetas. No afirma que UCI presente concept drift.
        result["y"] = result.y.map({"yes":"no","no":"yes"})
    elif name!="stable": raise ValueError("Escenario desconocido")
    return result

def drift_report(reference,current,name):
    from evidently import Report, Dataset, DataDefinition
    from evidently.presets import DataDriftPreset
    validate(reference); validate(current)
    definition=DataDefinition(numerical_columns=NUMERIC,categorical_columns=CATEGORICAL)
    ref=Dataset.from_pandas(reference[FEATURES],data_definition=definition)
    cur=Dataset.from_pandas(current[FEATURES],data_definition=definition)
    result=Report([DataDriftPreset()]).run(reference_data=ref,current_data=cur)
    REPORTS.mkdir(parents=True,exist_ok=True)
    result.save_html(str(REPORTS/f"drift_{name}.html"))
    result.save_json(str(REPORTS/f"drift_{name}.json"))
    return result

def fairness(frame, probability, threshold=.25):
    groups=pd.cut(frame.age,bins=[17,29,59,100],labels=["18-29","30-59","60-100"])
    result=[]
    for name in groups.cat.categories:
        mask=(groups==name).to_numpy(); y=(frame.loc[mask,"y"]=="yes").astype(int).to_numpy(); p=np.asarray(probability)[mask]
        if len(y)==0: result.append({"group":str(name),"n":0,"reliable":False}); continue
        pos=int(y.sum()); neg=int(len(y)-pos); pred=p>=threshold
        result.append({"group":str(name),"n":len(y),"positives":pos,"negatives":neg,"selection_rate":float(pred.mean()),
                       "tpr":float(pred[y==1].mean()) if pos else None,"fpr":float(pred[y==0].mean()) if neg else None,
                       "reliable":pos>=30 and neg>=30})
    return result

def delayed_performance(predictions,labels):
    required={"prediction_id","probability","model_version"}
    if not required.issubset(predictions): raise ValueError("Predicciones incompletas")
    if not {"prediction_id","target"}.issubset(labels): raise ValueError("Etiquetas incompletas")
    if predictions.prediction_id.duplicated().any() or labels.prediction_id.duplicated().any(): raise ValueError("Identificadores duplicados")
    if not labels.target.isin([0,1]).all(): raise ValueError("Etiqueta inválida")
    if not predictions.probability.between(0,1).all(): raise ValueError("Probabilidad inválida")
    merged=predictions.merge(labels,on="prediction_id",how="left",validate="one_to_one")
    result=[]
    for version,group in merged.groupby("model_version"):
        observed=group.dropna(subset=["target"])
        result.append({"model_version":version,"total":len(group),"labeled":len(observed),"coverage":len(observed)/len(group),
                       "metrics":metrics(observed.target.astype(int),observed.probability) if len(observed) else None})
    return result

def run(version="baseline-v1"):
    train,val,test=partitions(load()); model,meta=read_model(version)
    # Controles estables de la MISMA ventana, independientes; evaluación temporal separada.
    pool=val.sample(frac=1,random_state=SEED); reference=pool.iloc[:1500]; current=pool.iloc[1500:3000]
    results={"model_version":version,"note":"stable y shift son controles simulados de validación; test final separado"}
    for name in ["stable","shift","degraded"]:
        data=scenario(current,name); drift_report(reference,data,name)
        results[name]=metrics((data.y=="yes").astype(int),model.predict_proba(data[FEATURES])[:,1],meta["threshold"])
    p=model.predict_proba(test[FEATURES])[:,1]
    results["final_test"]=metrics((test.y=="yes").astype(int),p,meta["threshold"])
    results["fairness"]=fairness(test,p,meta["threshold"])
    REPORTS.mkdir(parents=True,exist_ok=True)
    (REPORTS/"monitoring.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    return results
