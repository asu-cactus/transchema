import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'x' to integer by rounding (since target schema expects integer)
df_all['x'] = df_all['x'].round().astype(int)

# Map 'label' strings to integers consistently
# Create a mapping from unique labels to integers
label_mapping = {label: idx+1 for idx, label in enumerate(sorted(df_all['label'].unique()))}
df_all['label'] = df_all['label'].map(label_mapping).astype(int)

# 'y' remains float as in target schema

# Reorder columns to match target schema exactly
df_all = df_all[['y', 'x', 'label']]

# Write output
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)