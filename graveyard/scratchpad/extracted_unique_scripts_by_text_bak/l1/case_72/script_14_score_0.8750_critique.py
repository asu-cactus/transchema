import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
df0 = df0.rename(columns={"click": "0"})
df0["condition"] = df0["condition"].astype(int)
df0["0"] = df0["0"].astype(int)

# Group by 'condition' and sum the '0' column
df_result = df0.groupby("condition", as_index=False).agg({"0": "sum"})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)