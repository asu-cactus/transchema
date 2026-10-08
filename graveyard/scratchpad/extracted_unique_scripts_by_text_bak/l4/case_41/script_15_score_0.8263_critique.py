import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

# Concatenate all sources (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Map labels to integers consistently across all sources
label_map = {label: idx+1 for idx, label in enumerate(sorted(df_all['label'].unique()))}
df_all['label'] = df_all['label'].map(label_map)

# Convert 'x' to integer (rounding to nearest int)
df_all['x'] = df_all['x'].round().astype(int)

# 'y' is float, keep as is
df_all['y'] = df_all['y'].astype(float)

# 'label' is integer, already mapped

# Reorder columns to match target schema: ['y', 'x', 'label']
result = df_all[['y', 'x', 'label']]

# Write to output file
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)