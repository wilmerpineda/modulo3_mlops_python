import json
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from bank_ops import data, model, lifecycle, monitor, api
from bank_ops.config import FEATURES

@pytest.fixture(scope="module")
def frame(): return data.load()

@pytest.fixture
def sandbox(tmp_path,monkeypatch):
    for module in [model,lifecycle]: monkeypatch.setattr(module,"ARTIFACTS",tmp_path/"artifacts")
    monkeypatch.setattr(api,"REPORTS",tmp_path/"reports")
    return tmp_path

def test_split_and_leakage(frame):
    train,val,test=data.partitions(frame)
    assert train.row_id.max()<val.row_id.min()<test.row_id.min()
    assert len(train)+len(val)+len(test)==len(frame)
    assert not {"duration","age","y","row_id","day"}&set(FEATURES)

@pytest.mark.parametrize("fault",["missing","null","target","campaign","empty"])
def test_invalid_data(frame,fault):
    f=frame.head().copy()
    if fault=="missing": f=f.drop(columns="balance")
    if fault=="null": f.loc[f.index[0],"balance"]=None
    if fault=="target": f.loc[f.index[0],"y"]="maybe"
    if fault=="campaign": f.loc[f.index[0],"campaign"]=-1
    if fault=="empty": f=f.iloc[:0]
    with pytest.raises(ValueError): data.validate(f)

def test_late_labels():
    pred=pd.DataFrame({"prediction_id":["a","b"],"probability":[.8,.1],"model_version":["v1","v1"]})
    labels=pd.DataFrame({"prediction_id":["a"],"target":[1]})
    result=monitor.delayed_performance(pred,labels)[0]
    assert result["coverage"]==.5 and result["metrics"]["roc_auc"] is None
    with pytest.raises(ValueError): monitor.delayed_performance(pred,pd.concat([labels,labels]))

def test_small_group():
    result=monitor.fairness(pd.DataFrame({"age":[20,22],"y":["no","no"]}),[.2,.3])
    assert result[0]["tpr"] is None and not result[0]["reliable"]

def test_unready_and_contract(sandbox,frame):
    with TestClient(api.create_app()) as client:
        assert client.get("/health").status_code==200
        assert client.get("/ready").status_code==503
        assert client.post("/predict",json={}).status_code==422
        assert client.post("/predict",json=frame.iloc[0][FEATURES].to_dict()).status_code==503

@pytest.mark.skip(reason="A3-02: implementar rechazo, promoción y rollback; retirar skip")
def test_promotion_rejection_and_rollback(sandbox,frame):
    # Comprobar versión HTTP y que el rechazo conserva el puntero.
    raise NotImplementedError("A3-02")

def test_checksum_tampering(sandbox):
    model.train("v1")
    with (sandbox/"artifacts"/"v1"/"model.joblib").open("ab") as f: f.write(b"tampered")
    with pytest.raises(ValueError): model.read_model("v1")
