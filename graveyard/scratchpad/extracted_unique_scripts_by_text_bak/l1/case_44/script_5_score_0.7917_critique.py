import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')

grouped = df0.groupby('Country / territory of asylum/residence', as_index=False)['Value'].sum()

grouped = grouped.rename(columns={'Value': 'Year'})

grouped['Year'] = grouped['Year'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)