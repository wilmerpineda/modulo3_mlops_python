import argparse, json
import pandas as pd
from .model import train
from .lifecycle import promote, rollback, compare
from .monitor import run, delayed_performance
def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="command",required=True)
    t=s.add_parser("train"); t.add_argument("--version",required=True); t.add_argument("--kind",choices=["baseline","candidate"],default="baseline")
    t=s.add_parser("promote"); t.add_argument("--version",required=True); t.add_argument("--actor",required=True); t.add_argument("--reason",required=True)
    t=s.add_parser("rollback"); t.add_argument("--actor",required=True); t.add_argument("--reason",required=True)
    t=s.add_parser("compare"); t.add_argument("--candidate",required=True); t.add_argument("--incumbent",required=True)
    t=s.add_parser("monitor"); t.add_argument("--version",default="baseline-v1")
    t=s.add_parser("labels"); t.add_argument("--predictions",required=True); t.add_argument("--labels",required=True)
    a=vars(p.parse_args()); command=a.pop("command")
    if command=="labels": result=delayed_performance(pd.read_json(a["predictions"],lines=True),pd.read_csv(a["labels"]))
    else: result={"train":train,"promote":promote,"rollback":rollback,"compare":compare,"monitor":run}[command](**a)
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
