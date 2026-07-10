import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_67/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_67/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_67/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df = pd.merge(df0, df1[['user_id', 'city']], on='user_id', how='inner')

df = df[['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test', 'price', 'converted', 'city']]

df['user_id'] = df['user_id'].astype(int)
df['test'] = df['test'].astype(int)
df['price'] = df['price'].astype(int)
df['converted'] = df['converted'].astype(int)
df['timestamp'] = df['timestamp'].astype(str)
df['source'] = df['source'].astype(str)
df['device'] = df['device'].astype(str)
df['operative_system'] = df['operative_system'].astype(str)
df['city'] = df['city'].astype(str)

df.to_csv(target_path, index=False)