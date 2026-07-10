import pandas as pd

# Since only one source table is given, we read it.
# If multiple source tables existed, we would read and union them here.

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

# If multiple source tables existed, union them like:
# dfs = [df0, df1, df2, ...]
# df = pd.concat(dfs, ignore_index=True)
# Here, only one source table is given, so df = df0

df = df0

result = df.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

result = result.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)