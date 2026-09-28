import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

# Concatenate all sources (union)
final_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Convert 'y' to integer
final_df['y'] = final_df['y'].astype(int)

# Encode 'label' as integer codes
final_df['label'] = final_df['label'].astype('category').cat.codes.astype(int)

# Ensure 'x' is float
final_df['x'] = final_df['x'].astype(float)

# Write to target file
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)