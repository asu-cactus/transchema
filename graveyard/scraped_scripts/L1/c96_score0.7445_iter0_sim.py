import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

df0_sub = df0[['Publisher']].copy()
df1_sub = df1[['hero_names']].copy()
# The target schema is ['Publisher'], integer type.
# df0 has 'Publisher' column with string values like 'DC Comics', 'Marvel Comics'.
# df1 has no 'Publisher' column, only 'hero_names' and many boolean columns.
# Since schemas differ and target only has 'Publisher' integer, we cannot union directly.
# But the plan says UNION of both sources, then GROUP_BY Publisher.
# However, df1 has no Publisher column, so union is not possible.
# We must reconsider.

# Re-examining the sources:
# Source0 has 'Publisher' column with string values.
# Source1 has no 'Publisher' column.
# Target schema is ['Publisher'] integer, with examples like 1,1,3.
# So likely the target is a count of occurrences per Publisher, with Publisher mapped to integer IDs.

# So the plan should be:
# 1) From Source0, group by Publisher, count rows per Publisher.
# 2) Map Publisher strings to integer IDs.
# 3) Source1 has no Publisher, so it cannot contribute to this aggregation.
# So only Source0 is relevant.

# Therefore, the correct plan is:
# GROUP_BY : [Publisher]
# NO_MORE_OPERATION

# Implementing that:

df_grouped = df0.groupby('Publisher').size().reset_index(name='count')

# Map Publisher strings to integer IDs starting from 1
publisher_map = {pub: idx+1 for idx, pub in enumerate(sorted(df_grouped['Publisher'].unique()))}
df_grouped['Publisher'] = df_grouped['Publisher'].map(publisher_map)

# The target schema is ['Publisher'] integer, and the examples show just the integer Publisher IDs.
# So output only the Publisher column (integer IDs), ignoring counts.

df_result = df_grouped[['Publisher']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)