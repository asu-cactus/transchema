import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_9/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_9/training_1.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on 'city'
df_joined = pd.merge(df1, df0, on='city', how='inner')

# Group by 'city' and sum 'driver_count'
result = df_joined.groupby('city', as_index=False)['driver_count'].sum()

result['driver_count'] = result['driver_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_9/target_multisource_mcts.csv", index=False)