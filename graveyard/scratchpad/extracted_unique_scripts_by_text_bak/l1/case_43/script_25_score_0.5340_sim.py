import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg_df = df0.groupby("facid").agg({
    "fac_type": "max",
    "fac_name": "max",
    "fac_address": "max",
    "city_state_zip": "max",
    "owner": "max",
    "operator": "max",
    "capacity": "sum"
}).reset_index()

agg_df["facid"] = agg_df["facid"].astype(int, errors='ignore')
agg_df["capacity"] = agg_df["capacity"].astype(int, errors='ignore')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)