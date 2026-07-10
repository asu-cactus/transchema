import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby("fac_type").agg({
    "facid": lambda x: pd.to_numeric(x, errors='coerce').min(),
    "capacity": "max",
    "fac_name": lambda x: pd.to_numeric(x, errors='coerce').min(),
    "fac_address": lambda x: pd.to_numeric(x, errors='coerce').min(),
    "city_state_zip": lambda x: pd.to_numeric(x, errors='coerce').min(),
    "owner": lambda x: pd.to_numeric(x, errors='coerce').min(),
    "operator": lambda x: pd.to_numeric(x, errors='coerce').min()
}).reset_index()

agg["facid"] = agg["facid"].fillna(0).astype(int)
agg["capacity"] = agg["capacity"].fillna(0).astype(int)
agg["fac_name"] = agg["fac_name"].fillna(0).astype(int)
agg["fac_address"] = agg["fac_address"].fillna(0).astype(int)
agg["city_state_zip"] = agg["city_state_zip"].fillna(0).astype(int)
agg["owner"] = agg["owner"].fillna(0).astype(int)
agg["operator"] = agg["operator"].fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)