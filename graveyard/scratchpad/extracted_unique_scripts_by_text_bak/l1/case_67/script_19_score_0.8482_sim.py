import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

melted = pd.melt(df, id_vars=['user_id'], value_vars=['sad.depressed', 'open.stressed'], var_name='variable', value_name='value')

melted['variable'] = melted['variable'].map({'sad.depressed': 'sad', 'open.stressed': 'stressed'})

result = melted.pivot_table(index='user_id', columns='variable', values='value', aggfunc='mean').reset_index()

result = result[['user_id', 'sad', 'stressed']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)