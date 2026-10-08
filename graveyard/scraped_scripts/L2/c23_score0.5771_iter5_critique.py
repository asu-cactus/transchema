import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0[['city']], df1[['city', 'driver_count']], on='city', how='inner')

result = merged.rename(columns={'driver_count': 'type'})[['city', 'type']]

result.to_csv(target_path, index=False)