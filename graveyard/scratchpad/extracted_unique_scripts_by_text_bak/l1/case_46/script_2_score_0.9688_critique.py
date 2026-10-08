import pandas as pd
import glob

file_pattern = "autopipeline-benchmarks/github-pipelines/length1_46/training_*.csv"
files = glob.glob(file_pattern)

df_list = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

df_grouped = df_all.groupby('Text Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

df_grouped = df_grouped.rename(columns={'Text Date': 'Date'})

df_grouped['Water Use'] = df_grouped['Water Use'].astype(float)
df_grouped['Power Use'] = df_grouped['Power Use'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)