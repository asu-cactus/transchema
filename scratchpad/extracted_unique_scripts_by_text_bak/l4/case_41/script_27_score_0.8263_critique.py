import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'x' to integer by rounding
df_all['x'] = df_all['x'].round().astype(int)

# Encode 'label' as integer codes consistently
df_all['label'] = df_all['label'].astype('category').cat.codes.astype(int)

# Keep 'y' as float (no change)

# Reorder columns to match target schema: ['y', 'x', 'label']
df_all = df_all[['y', 'x', 'label']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)