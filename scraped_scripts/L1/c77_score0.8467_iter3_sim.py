import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="fac_type")

result = joined.groupby("fac_type", as_index=False)["capacity_x"].sum()
result.columns = ["fac_type", "capacity"]
result["capacity"] = result["capacity"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)