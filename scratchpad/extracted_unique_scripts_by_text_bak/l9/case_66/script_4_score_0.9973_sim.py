import pandas as pd

src_paths = {
    "Source9_66_0": "autopipeline-benchmarks/github-pipelines/length9_66/training_0.csv",
    "Source9_66_1": "autopipeline-benchmarks/github-pipelines/length9_66/training_1.csv",
    "Source9_66_2": "autopipeline-benchmarks/github-pipelines/length9_66/training_2.csv",
    "Source9_66_3": "autopipeline-benchmarks/github-pipelines/length9_66/training_3.csv",
    "Source9_66_4": "autopipeline-benchmarks/github-pipelines/length9_66/training_4.csv",
    "Source9_66_5": "autopipeline-benchmarks/github-pipelines/length9_66/training_5.csv",
    "Source9_66_6": "autopipeline-benchmarks/github-pipelines/length9_66/training_6.csv",
    "Source9_66_7": "autopipeline-benchmarks/github-pipelines/length9_66/training_7.csv",
    "Source9_66_8": "autopipeline-benchmarks/github-pipelines/length9_66/training_8.csv",
    "Source9_66_9": "autopipeline-benchmarks/github-pipelines/length9_66/training_9.csv",
}

df0 = pd.read_csv(src_paths["Source9_66_0"], index_col=0)
df3 = pd.read_csv(src_paths["Source9_66_3"], index_col=0)

join_cols = ['admit', 'gre', 'gpa', 'prestige']
df_joined = pd.merge(df0, df3, on=join_cols, how='inner', suffixes=('_0', '_3'))

# The join on all columns means only rows exactly matching in both tables are kept.
# The join result schema is the same as the join columns (no extra columns).
# According to the plan, next is UNION of all sources except Source9_66_3 (which was joined with Source9_66_0).
# But the plan UNION includes Source9_66_0 again, so we must union the joined result with all other sources except Source9_66_3.

# Load all other sources except Source9_66_3
dfs_union = []
for i in range(10):
    if i == 3:
        continue
    df = pd.read_csv(src_paths[f"Source9_66_{i}"], index_col=0)
    dfs_union.append(df)

# Union all these sources (including Source9_66_0 again)
df_union = pd.concat(dfs_union, ignore_index=True)

# The join result is a subset of Source9_66_0 rows that exactly match Source9_66_3 rows.
# The union includes all Source9_66_0 rows again, so the join result is effectively redundant for final union.
# The partial plan is ambiguous here, but since the join is first operation and union second,
# and the union includes Source9_66_0, the final target is the union of all sources.
# So the join is likely a filtering step or a check, but final output is union of all sources.

# Therefore, final target is union of all sources (including Source9_66_0 and Source9_66_3).
# Load Source9_66_3 and add to union
df3_full = pd.read_csv(src_paths["Source9_66_3"], index_col=0)
df_union = pd.concat([df_union, df3_full], ignore_index=True)

# Ensure correct dtypes as per target schema
df_union['admit'] = df_union['admit'].astype(int)
df_union['gre'] = df_union['gre'].astype(int)
df_union['gpa'] = df_union['gpa'].astype(float)
df_union['prestige'] = df_union['prestige'].astype(int)

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)