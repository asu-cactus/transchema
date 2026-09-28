import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

df_pivot = df0.pivot_table(index='customer_id', columns='date', values='amount', aggfunc='sum').reset_index()

df_melted = df_pivot.melt(id_vars=['customer_id'], var_name='date', value_name='amount')

result = df_melted[['customer_id', 'date']].dropna().astype({'customer_id': int, 'date': str})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)