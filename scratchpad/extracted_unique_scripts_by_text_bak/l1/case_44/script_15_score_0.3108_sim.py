import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df = df0[['Country / territory of asylum/residence', 'Year', 'Value']].copy()
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df.dropna(subset=['Year'])
df['Year'] = df['Year'].astype(int)

grouped = df.groupby(['Country / territory of asylum/residence', 'Year'], as_index=False)['Value'].sum()

grouped.rename(columns={'Value': 'Year'}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)