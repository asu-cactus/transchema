import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

grouped = df_all.groupby('TransTo', dropna=False).agg(
    WarNum_count = ('WarNum', 'count'),
    WarNum_min = ('WarNum', 'min'),
    WarNum_max = ('WarNum', 'max')
).reset_index()

# The target schema is ['TransTo', 'WarNum'] with WarNum as integer.
# The partial plan suggests aggregations on WarNum, but target has only one WarNum column.
# From the target examples, WarNum seems to be a sequence number (1,2,3,...).
# Since the partial plan is ambiguous about which aggregation to keep, and target examples show WarNum as integer,
# we will produce one row per TransTo with WarNum as the count of WarNum occurrences (or min/max).
# The best guess is to use the count of WarNum as WarNum in target, since target examples show WarNum increasing with TransTo.

# Drop NaN TransTo rows because target examples have no NaN TransTo
grouped = grouped[grouped['TransTo'].notna()]

# Convert TransTo to integer (target schema)
grouped['TransTo'] = grouped['TransTo'].astype(int)

# Use WarNum_count as WarNum in target
grouped['WarNum'] = grouped['WarNum_count'].astype(int)

result = grouped[['TransTo', 'WarNum']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)