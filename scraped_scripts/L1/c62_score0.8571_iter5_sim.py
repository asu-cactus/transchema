import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df_grouped = df.groupby('Text Date', as_index=False).agg({
    'Water Use': 'sum',
    'Power Use': 'sum'
})

df_grouped = df_grouped.rename(columns={'Text Date': 'Month', 'Power Use': 'Power Use', 'Water Use': 'Water Use'})

df_grouped['Month'] = df_grouped['Month'].astype(str)
df_grouped['Water Use'] = df_grouped['Water Use'].astype(float)
df_grouped['Power Use'] = df_grouped['Power Use'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)