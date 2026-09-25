import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df = df0[['Text Date', 'Water Use', 'Power Use']].copy()
df.rename(columns={'Text Date': 'Date'}, inplace=True)

# Convert types explicitly
df['Water Use'] = df['Water Use'].astype(float)
df['Power Use'] = df['Power Use'].astype(int)

# Group by Date and sum Water Use and Power Use
df_grouped = df.groupby('Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)