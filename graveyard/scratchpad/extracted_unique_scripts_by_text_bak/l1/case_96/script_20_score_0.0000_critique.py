import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

# Join on hero name
df_joined = pd.merge(df0, df1, left_on='name', right_on='hero_names', how='inner')

# Group by Publisher and count number of heroes (name)
result = df_joined.groupby('Publisher', dropna=False).agg({'name':'count'}).reset_index()

# Rename count column to 'Publisher' to match target schema
result.columns = ['Publisher', 'Publisher']

# The target 'Publisher' column is integer, so convert
result['Publisher'] = result['Publisher'].astype(int)

# Since the count column and group by column have same name, keep only the count column
# Actually, the above renaming made both columns named 'Publisher', so keep only the count column
# So select the second 'Publisher' column (the count)
result = result[['Publisher']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)