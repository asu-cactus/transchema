import pandas as pd

# List all source files (assuming two source files as example)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_84/training_1.csv"
]

dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    # Extract substring before '*'
    df['V_GENE'] = df['V_CALL'].str.split('*').str[0]
    dfs.append(df[['V_GENE']])

# Union all dataframes (concatenate)
result = pd.concat(dfs, ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)