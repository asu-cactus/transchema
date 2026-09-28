import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_99/training_0.csv", index_col=0)

# Reorder columns to match target schema exactly
df0 = df0[['user_id', 'timestamp', 'source', 'device', 'operative_system', 'test', 'price', 'converted']]

# Ensure correct dtypes matching target schema
df0['user_id'] = df0['user_id'].astype(int)
df0['timestamp'] = df0['timestamp'].astype(str)
df0['source'] = df0['source'].astype(str)
df0['device'] = df0['device'].astype(str)
df0['operative_system'] = df0['operative_system'].astype(str)
df0['test'] = df0['test'].astype(int)
df0['price'] = df0['price'].astype(int)
df0['converted'] = df0['converted'].astype(int)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_99/target_multisource_mcts.csv", index=False)