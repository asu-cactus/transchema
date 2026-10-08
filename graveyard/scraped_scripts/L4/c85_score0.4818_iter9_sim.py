import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

# The partial plan suggests joining Source4_85_0 with itself on crit_cn, then unioning the two.
# But joining a table with itself on crit_cn will just duplicate rows with the same crit_cn.
# Since the source is only one table, unioning it with itself is redundant.
# Instead, we just need to select the relevant columns and convert types to match target schema.

# Select relevant columns
df = df0[['crit_cn', 'critic']].copy()

# Convert 'critic' to integer if not already
df['critic'] = pd.to_numeric(df['critic'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)