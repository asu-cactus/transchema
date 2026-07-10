import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_44/training_0.csv", index_col=0)

agg_df = df.groupby('Country / territory of asylum/residence', as_index=False)['Value'].sum()

agg_df = agg_df.rename(columns={'Value': 'Year'})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_44/target_multisource_mcts.csv", index=False)