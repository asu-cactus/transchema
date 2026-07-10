import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv"

df0_1 = pd.read_csv(source0_path, index_col=0)
df0_2 = pd.read_csv(source0_path, index_col=0)
union_result = pd.concat([df0_1, df0_2], ignore_index=True)

df1 = pd.read_csv(source1_path, index_col=0)

merged = union_result.merge(df1[['item_id', 'movie title']], on='item_id', how='left')

merged = merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

merged.to_csv(target_path, index=False)