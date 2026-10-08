import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

# If there were multiple source tables, we would union them here.
# Since only one source table is given, just use df0 directly.

grouped = df0.groupby("Gender").agg({"Purchase ID": "count"}).reset_index()
grouped.columns = ["Gender", "0"]
grouped["Gender"] = grouped["Gender"].astype(str)
grouped["0"] = grouped["0"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)