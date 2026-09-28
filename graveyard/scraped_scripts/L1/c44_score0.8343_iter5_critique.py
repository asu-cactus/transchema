import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)
df0['Value'] = pd.to_numeric(df0['Value'], errors='coerce')
result = df0.groupby(['Country / territory of asylum/residence'], as_index=False)['Value'].sum()
result = result.rename(columns={'Value': 'Year'})
result['Year'] = result['Year'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)