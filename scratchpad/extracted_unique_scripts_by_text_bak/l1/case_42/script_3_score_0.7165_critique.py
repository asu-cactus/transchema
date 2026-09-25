import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df_merged = pd.merge(df0, df1[['item_id', 'movie title']], on='item_id', how='left')

df_merged = df_merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

df_merged.to_csv(target_path, index=False)