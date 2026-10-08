import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY WhereFought and aggregate WarNum by min to get unique WarNum per WhereFought
result = df_all.groupby("WhereFought", as_index=False)["WarNum"].min()

# Ensure correct dtypes as per target schema
result["WhereFought"] = result["WhereFought"].astype(int)
result["WarNum"] = result["WarNum"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)