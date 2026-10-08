import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Factorize 'label' to integer codes starting from 1
df['label'] = pd.factorize(df['label'].astype(str))[0] + 1

# Set 'x' column to integer 1 as in target schema
df['x'] = 1

# 'y' column remains as float from source

# Select columns in target schema order: ['y', 'x', 'label']
result = df[['y', 'x', 'label']].copy()

# Ensure correct dtypes
result['y'] = result['y'].astype(float)
result['x'] = result['x'].astype(int)
result['label'] = result['label'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)