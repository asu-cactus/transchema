import pandas as pd

# Read the source table(s)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

# If there were multiple source tables, we would union them here, e.g.:
# dfs = [df0, df1, df2, ...]
# df = pd.concat(dfs, ignore_index=True)
# Since only one source table is given, just use df0
df = df0

# Group by Gender and count occurrences
result = df.groupby("Gender").size().reset_index(name="0")

# Ensure types match target schema
result["Gender"] = result["Gender"].astype(str)
result["0"] = result["0"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)