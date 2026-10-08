import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

melted = pd.melt(df, id_vars=['user_id'], value_vars=['sad.depressed', 'open.stressed'], var_name='emotion', value_name='value')

pivoted = melted.pivot_table(index='user_id', columns='emotion', values='value', aggfunc='mean').reset_index()

pivoted.columns = ['user_id', 'sad', 'stressed']

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)