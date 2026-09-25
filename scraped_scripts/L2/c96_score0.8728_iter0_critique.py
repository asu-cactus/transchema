import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_96/training_1.csv", index_col=0)

# Rename columns to align join keys
df1 = df1.rename(columns={"cop": "cop_name"})

# Perform inner join on cop_name, day, and fname
df_joined = pd.merge(df0, df1, how="inner", on=["cop_name", "day", "fname"])

# Group by fname and count rows
result = df_joined.groupby("fname", as_index=False).size().rename(columns={"size": "row_count"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_96/target_multisource_mcts.csv", index=False)