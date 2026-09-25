import pandas as pd

src_paths = {
    "Source9_91_0": "autopipeline-benchmarks/github-pipelines/length9_91/training_0.csv",
    "Source9_91_1": "autopipeline-benchmarks/github-pipelines/length9_91/training_1.csv",
    "Source9_91_2": "autopipeline-benchmarks/github-pipelines/length9_91/training_2.csv",
    "Source9_91_3": "autopipeline-benchmarks/github-pipelines/length9_91/training_3.csv",
    "Source9_91_4": "autopipeline-benchmarks/github-pipelines/length9_91/training_4.csv",
    "Source9_91_5": "autopipeline-benchmarks/github-pipelines/length9_91/training_5.csv",
    "Source9_91_6": "autopipeline-benchmarks/github-pipelines/length9_91/training_6.csv",
    "Source9_91_7": "autopipeline-benchmarks/github-pipelines/length9_91/training_7.csv",
    "Source9_91_8": "autopipeline-benchmarks/github-pipelines/length9_91/training_8.csv",
    "Source9_91_9": "autopipeline-benchmarks/github-pipelines/length9_91/training_9.csv",
}

df_0 = pd.read_csv(src_paths["Source9_91_0"], index_col=0)
df_5 = pd.read_csv(src_paths["Source9_91_5"], index_col=0)

# Join Source9_91_0 and Source9_91_5 on all columns (inner join on all columns means intersection)
# But the partial plan shows join on all columns, which is effectively intersection of rows present in both.
# To do this, merge on all columns:
join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_join = pd.merge(df_0, df_5, on=join_cols, how='inner')

# Load all other sources except 5 (already used in join)
dfs_union = []
for i in [0,1,2,3,4,6,7,8,9]:
    dfs_union.append(pd.read_csv(src_paths[f"Source9_91_{i}"], index_col=0))

# Union all these sources (concatenate)
df_union = pd.concat(dfs_union, ignore_index=True)

# The partial plan suggests union of these sources after join of 0 and 5.
# But join result is intersection of 0 and 5 rows.
# The union sources include 0 again, so to combine join and union results, we need to union join result with union result excluding 0 to avoid duplicates.

# Remove Source9_91_0 from union dfs to avoid duplicate rows from df_0
dfs_union_excl_0 = []
for i in [1,2,3,4,6,7,8,9]:
    dfs_union_excl_0.append(pd.read_csv(src_paths[f"Source9_91_{i}"], index_col=0))
df_union_excl_0 = pd.concat(dfs_union_excl_0, ignore_index=True)

# Final dataframe is union of join result and union excluding 0
df_final = pd.concat([df_join, df_union_excl_0], ignore_index=True)

# Ensure columns and types match target schema
df_final = df_final[['admit', 'gre', 'gpa', 'prestige']]
df_final = df_final.astype({'admit': 'int64', 'gre': 'int64', 'gpa': 'float64', 'prestige': 'int64'})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_91/target_multisource_mcts.csv", index=False)