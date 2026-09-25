import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

df_grouped = df.groupby('Value Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

df_grouped.rename(columns={'Value Date': 'Date'}, inplace=True)
df_grouped['Water Use'] = df_grouped['Water Use'].astype(float)
df_grouped['Power Use'] = df_grouped['Power Use'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)