import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_77/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_77/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_77/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on city (inner join)
joined = pd.merge(df0, df1[['city']], how='inner', on='city')

# Group by city and sum driver_count (driver_count is unique per city in df0, but sum ensures correctness)
final = joined.groupby('city', as_index=False)['driver_count'].sum()

final.to_csv(target_path, index=False)