import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)
df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')

agg = df0.groupby('Country / territory of asylum/residence', dropna=False)['Value'].sum().reset_index()
agg.rename(columns={'Value': 'Year'}, inplace=True)
agg['Year'] = agg['Year'].fillna(0).astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)