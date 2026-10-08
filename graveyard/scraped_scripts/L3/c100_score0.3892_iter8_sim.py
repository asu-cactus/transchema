import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

merged = pd.merge(df0, df2, left_on="Country", right_on="Country Name")

id_vars = ['Rank']
value_vars = [col for col in merged.columns if col.isdigit()]
pivoted = merged.melt(id_vars=id_vars, value_vars=value_vars, var_name='0', value_name='value')

pivoted['0'] = pivoted['0'].astype(int)
pivoted['Rank'] = pivoted['Rank'].astype(int)
pivoted['value'] = pivoted['value'].fillna(0).astype(int)

result = pivoted[['Rank', '0', 'value']].rename(columns={'value': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)