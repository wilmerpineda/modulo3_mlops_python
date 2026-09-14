import os
from pathlib import Path
ROOT = Path(os.getenv("BANK_ROOT", Path(__file__).resolve().parents[2]))
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
REPORTS = ROOT / "reports"
NUMERIC = ["balance", "campaign", "pdays", "previous"]
CATEGORICAL = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
FEATURES = NUMERIC + CATEGORICAL
SEED = 42
THRESHOLD = 0.25
