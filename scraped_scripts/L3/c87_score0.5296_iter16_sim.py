import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_2.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_87/training_1.csv", index_col=0)

df1_sub = df1[['Rank', 'Country']]
df2_sub = df2.rename(columns={'Country': 'Country'})

df2_sub['Rank'] = pd.NA
df2_sub = df2_sub[['Rank', 'Country']]

union_df = pd.concat([df1_sub, df2_sub], ignore_index=True)

union_df = union_df.dropna(subset=['Rank'])

pivot_df = union_df.pivot_table(index='Rank', columns='Country', aggfunc='size', fill_value=0)

pivot_df = pivot_df.reset_index()

pivot_df.columns.name = None

pivot_df = pivot_df.rename(columns={pivot_df.columns[1]: '0'})

result = pivot_df[['Rank', '0']].copy()

result['Rank'] = result['Rank'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_87/target_multisource_mcts.csv", index=False)