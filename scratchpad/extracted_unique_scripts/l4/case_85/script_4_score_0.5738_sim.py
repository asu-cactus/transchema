import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv"
df0 = pd.read_csv(source_path, index_col=0)

# First operation: join Source4_85_0 with itself on crit_cn (self-join)
df_joined = pd.merge(df0, df0, on="crit_cn", suffixes=('_left', '_right'))

# Second operation: union Source4_85_0 with itself (concatenate)
df_union = pd.concat([df0, df0], ignore_index=True)

# The target schema is ['crit_cn': string, 'critic': integer]
# From the union, select only the columns needed for the target
df_result = df_union[['crit_cn', 'critic']].copy()

# Convert 'critic' to integer if not already
df_result['critic'] = pd.to_numeric(df_result['critic'], errors='coerce').fillna(0).astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)