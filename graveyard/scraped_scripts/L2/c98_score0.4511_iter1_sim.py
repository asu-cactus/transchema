import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_98/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_98/training_1.csv", index_col=0)

# Source0 schema: ['city', 'driver_count', 'type'] - no 'fare' column, cannot union with Source1
# Source1 schema: ['city', 'date', 'fare', 'ride_id'] - matches target columns partially, contains 'fare'

# The target schema is ['city', 'fare'].
# Only Source1 contains 'fare' column.
# So we take Source1, select 'city' and 'fare' columns, convert fare to float.

target_df = df2[['city', 'fare']].copy()
target_df['fare'] = target_df['fare'].astype(float)

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_98/target_multisource_mcts.csv", index=False)