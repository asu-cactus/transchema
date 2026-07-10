import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df = df0[['Country / territory of asylum/residence', 'Value']].copy()
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
df = df.dropna(subset=['Value'])

grouped = df.groupby('Country / territory of asylum/residence', as_index=False)['Value'].sum()
grouped.rename(columns={'Value': 'Year'}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)