import pandas as pd
import glob

# Read all source files matching the pattern (assuming 5 source files as an example)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_84/training_*.csv"
file_list = sorted(glob.glob(file_pattern))

dfs = []
for file in file_list:
    df = pd.read_csv(file, index_col=0)
    df['V_GENE'] = df['V_CALL'].str.split('*').str[0]
    dfs.append(df[['V_GENE']])

result = pd.concat(dfs, ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)