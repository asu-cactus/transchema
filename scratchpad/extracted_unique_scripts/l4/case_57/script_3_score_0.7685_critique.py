import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

# UNION all source tables
union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Drop rows where TransTo is NaN because target schema requires integer TransTo
union_df = union_df.dropna(subset=['TransTo'])

# Convert TransTo and WarNum to integer type (Int64 to allow NA if any)
union_df = union_df.astype({'TransTo': 'Int64', 'WarNum': 'Int64'})

# GROUP BY TransTo, aggregate WarNum by taking the first value
result = union_df.groupby('TransTo', as_index=False).agg({'WarNum': 'first'})

# Ensure column order matches target schema: ['TransTo', 'WarNum']
result = result[['TransTo', 'WarNum']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)