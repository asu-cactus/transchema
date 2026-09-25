import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df0["facid"] = pd.to_numeric(df0["facid"], errors='coerce').fillna(0).astype(int)
df0["capacity"] = pd.to_numeric(df0["capacity"], errors='coerce').fillna(0).astype(int)
df0["fac_name"] = df0["fac_name"].astype(str).apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0).astype(int)
df0["fac_address"] = df0["fac_address"].astype(str).apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0).astype(int)
df0["city_state_zip"] = df0["city_state_zip"].astype(str).apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0).astype(int)
df0["owner"] = df0["owner"].astype(str).apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0).astype(int)
df0["operator"] = df0["operator"].astype(str).apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0).astype(int)
df0["fac_type"] = df0["fac_type"].astype(str)

df0 = df0[["fac_type", "facid", "capacity", "fac_name", "fac_address", "city_state_zip", "owner", "operator"]]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)