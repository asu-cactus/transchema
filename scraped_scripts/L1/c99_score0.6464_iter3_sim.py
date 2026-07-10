import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['user_id'] = df['user_id'].astype(int)
df['timestamp'] = df['timestamp'].astype(str)
df['source'] = df['source'].astype(str)
df['device'] = df['device'].astype(str)
df['operative_system'] = df['operative_system'].astype(str)
df['test'] = df['test'].astype(int)
df['price'] = df['price'].astype(int)
df['converted'] = df['converted'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)