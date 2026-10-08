import pandas as pd

# Since only one source table is given, we read it.
# If there were multiple source tables, we would read and concat them here.
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_19/training_0.csv", index_col=0)

# Convert is_goal to numeric, coercing errors to NaN
df0['is_goal'] = pd.to_numeric(df0['is_goal'], errors='coerce')

# UNION step: if multiple source tables existed, we would concat them here.
# For now, just use df0 as the unioned dataframe.
df_union = df0.copy()

# GROUP BY shot_basics and is_goal
grouped = df_union.groupby(['shot_basics', 'is_goal'], dropna=False).agg(
    shot_basics_sum=('shot_basics', 'size'),  # count of rows per group
    is_goal_count1=('is_goal', 'count')       # count of non-null is_goal per group
).reset_index()

# Ensure types match target schema
grouped['shot_basics_sum'] = grouped['shot_basics_sum'].astype(int)
grouped['is_goal_count1'] = grouped['is_goal_count1'].astype(int)

# The target schema is ['shot_basics', 'is_goal', 'shot_basics_sum', 'is_goal_count1']
result = grouped[['shot_basics', 'is_goal', 'shot_basics_sum', 'is_goal_count1']]

# Write to output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_19/target_multisource_mcts.csv", index=False)