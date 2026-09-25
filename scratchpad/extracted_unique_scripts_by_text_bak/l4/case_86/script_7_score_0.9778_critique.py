import pandas as pd

# Read all source CSV files with index_col=0 to ignore the numerical index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv", index_col=0)

# Concatenate all sources vertically (UNION)
result = pd.concat([source0, source1, source2, source3, source4], ignore_index=True)

# Write the final output with exact column names as target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)