import hashlib, json, platform, subprocess
from datetime import datetime, timezone
import joblib, numpy as np, sklearn
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score, precision_score, recall_score, f1_score, brier_score_loss, confusion_matrix
from .config import NUMERIC, CATEGORICAL, FEATURES, THRESHOLD, ARTIFACTS, DATA, SEED
from .data import digest, load, partitions

def pipeline(kind="baseline"):
    prep=ColumnTransformer([("num",StandardScaler(),NUMERIC), ("cat",OneHotEncoder(handle_unknown="ignore"),CATEGORICAL)])
    estimator=LogisticRegression(max_iter=2000, random_state=SEED) if kind=="baseline" else RandomForestClassifier(n_estimators=120, min_samples_leaf=15, max_depth=12, n_jobs=2, random_state=SEED)
    return Pipeline([("features",prep),("model",estimator)])

def metrics(y, probability, threshold=THRESHOLD):
    y=np.asarray(y); p=np.asarray(probability); prediction=(p>=threshold).astype(int)
    if len(y)==0: raise ValueError("No hay etiquetas")
    both=len(np.unique(y))==2
    return {"n":len(y), "prevalence":float(y.mean()), "average_precision":float(average_precision_score(y,p)) if both else None,
            "roc_auc":float(roc_auc_score(y,p)) if both else None, "precision":float(precision_score(y,prediction,zero_division=0)),
            "recall":float(recall_score(y,prediction,zero_division=0)), "f1":float(f1_score(y,prediction,zero_division=0)),
            "brier":float(brier_score_loss(y,p)), "confusion_matrix":confusion_matrix(y,prediction,labels=[0,1]).tolist(), "threshold":threshold}

def train(version="baseline-v1", kind="baseline"):
    if not version or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in version): raise ValueError("Versión no válida")
    destination=ARTIFACTS/version
    if destination.exists(): raise ValueError("Versión inmutable ya existente: elija otra")
    train_df,val,_=partitions(load())
    estimator=pipeline(kind); estimator.fit(train_df[FEATURES],(train_df.y=="yes").astype(int))
    score=metrics((val.y=="yes").astype(int),estimator.predict_proba(val[FEATURES])[:,1])
    destination.mkdir(parents=True)
    joblib.dump(estimator,destination/"model.joblib")
    try: commit=subprocess.check_output(["git","rev-parse","HEAD"],stderr=subprocess.DEVNULL,text=True).strip()
    except (OSError, subprocess.CalledProcessError): commit="sin-repositorio"
    meta={"version":version,"kind":kind,"created_utc":datetime.now(timezone.utc).isoformat(),"features":FEATURES,"threshold":THRESHOLD,
          "data_sha256":digest(DATA/"bank-full.csv"),"model_sha256":digest(destination/"model.joblib"),"git_commit":commit,
          "python":platform.python_version(),"sklearn":sklearn.__version__,"seed":SEED,"train_rows":len(train_df),"validation":score,
          "split":"ordered-60-20-20", "excluded":["duration","age","day"], "educational_only":True}
    (destination/"metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    return meta

def read_model(version):
    if not version or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in version): raise ValueError("Versión no válida")
    folder=ARTIFACTS/version; meta=json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
    if meta["features"] != FEATURES or digest(folder/"model.joblib") != meta["model_sha256"]: raise ValueError("Artefacto incompatible o alterado")
    # Cargar únicamente artefactos propios: joblib no es un formato seguro para archivos ajenos.
    return joblib.load(folder/"model.joblib"),meta
