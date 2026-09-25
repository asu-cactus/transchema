import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_77/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_77/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_77/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

groupby_1 = df1.groupby('city', as_index=False).size().rename(columns={'size': 'ride_count'})

join_result = pd.merge(df0, groupby_1, how='inner', on='city')

final = join_result.groupby('city', as_index=False)['driver_count'].sum()

final.to_csv(target_path, index=False)