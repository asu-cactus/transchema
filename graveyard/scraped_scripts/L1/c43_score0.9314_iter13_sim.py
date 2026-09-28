import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby("fac_type").agg({
    "facid": "min",
    "capacity": "max",
    "fac_name": "min",
    "fac_address": "min",
    "city_state_zip": "min",
    "owner": "min",
    "operator": "min"
}).reset_index()

agg["facid"] = pd.to_numeric(agg["facid"], errors='coerce').fillna(0).astype(int)
agg["capacity"] = pd.to_numeric(agg["capacity"], errors='coerce').fillna(0).astype(int)
agg["fac_name"] = pd.to_numeric(agg["fac_name"], errors='coerce').fillna(0).astype(int)
agg["fac_address"] = pd.to_numeric(agg["fac_address"], errors='coerce').fillna(0).astype(int)
agg["city_state_zip"] = pd.to_numeric(agg["city_state_zip"], errors='coerce').fillna(0).astype(int)
agg["owner"] = pd.to_numeric(agg["owner"], errors='coerce').fillna(0).astype(int)
agg["operator"] = pd.to_numeric(agg["operator"], errors='coerce').fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)