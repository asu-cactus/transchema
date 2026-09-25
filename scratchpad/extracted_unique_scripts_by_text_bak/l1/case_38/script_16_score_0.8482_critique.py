import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

melted = pd.melt(df, id_vars=['user_id'], value_vars=['sad.depressed', 'open.stressed'], var_name='emotion', value_name='value')

# Rename emotion values to match target column names
melted['emotion'] = melted['emotion'].map({'sad.depressed': 'sad', 'open.stressed': 'stressed'})

pivoted = melted.pivot_table(index='user_id', columns='emotion', values='value', aggfunc='mean').reset_index()

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)