import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

# Lowercase user_id to match target examples
df0['user_id'] = df0['user_id'].str.lower()

# Ensure columns are in the correct order and types as target schema
df0 = df0[['user_id', 'email', 'geo']]

df0['user_id'] = df0['user_id'].astype(str)
df0['email'] = df0['email'].astype(str)
df0['geo'] = df0['geo'].astype(str)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)