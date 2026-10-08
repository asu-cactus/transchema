import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df["facid"] = pd.to_numeric(df["facid"], errors='coerce').fillna(0).astype(int)
df["capacity"] = pd.to_numeric(df["capacity"], errors='coerce').fillna(0).astype(int)
df["fac_name"] = pd.to_numeric(df["fac_name"], errors='coerce').fillna(0).astype(int)
df["fac_address"] = pd.to_numeric(df["fac_address"], errors='coerce').fillna(0).astype(int)
df["city_state_zip"] = pd.to_numeric(df["city_state_zip"], errors='coerce').fillna(0).astype(int)
df["owner"] = pd.to_numeric(df["owner"], errors='coerce').fillna(0).astype(int)
df["operator"] = pd.to_numeric(df["operator"], errors='coerce').fillna(0).astype(int)

df = df[["fac_type", "facid", "capacity", "fac_name", "fac_address", "city_state_zip", "owner", "operator"]]

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)