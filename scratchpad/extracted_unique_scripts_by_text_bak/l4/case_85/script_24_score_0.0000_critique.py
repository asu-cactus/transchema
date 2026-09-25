import pandas as pd

# Read all source files (assuming 4 source files as per typical naming)
dfs = []
for i in range(4):
    df = pd.read_csv(f"autopipeline-benchmarks/github-pipelines/length4_85/training_{i}.csv", index_col=0)
    dfs.append(df)

# UNION all source tables
df_union = pd.concat(dfs, ignore_index=True)

# GROUP BY crit_cn and sum critic
df_grouped = df_union.groupby("crit_cn", as_index=False)["critic"].sum()

# Ensure types match target schema
df_grouped["crit_cn"] = df_grouped["crit_cn"].astype(str)
df_grouped["critic"] = df_grouped["critic"].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)