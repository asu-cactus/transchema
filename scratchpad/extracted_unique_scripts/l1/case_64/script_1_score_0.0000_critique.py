import pandas as pd

# Read source tables
source0_path = "autopipeline-benchmarks/github-pipelines/length1_64/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_64/training_1.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Perform full outer join on name = hero_names
df_merged = pd.merge(df0, df1, how='outer', left_on='name', right_on='hero_names')

# Write output to target path
output_path = "autopipeline-benchmarks/github-pipelines/length1_64/target_multisource_mcts.csv"
df_merged.to_csv(output_path, index=False)