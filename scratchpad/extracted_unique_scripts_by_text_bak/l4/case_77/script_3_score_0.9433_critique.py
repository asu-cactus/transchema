import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Join Source4_77_1 and Source4_77_2 on school name
df1_2 = pd.merge(df1, df2, how='inner', left_on='name', right_on='school')

# Join the above with Source4_77_0 on school name
df_all = pd.merge(df0, df1_2, how='inner', left_on='school', right_on='name')

# Group by all target columns except index, no aggregation needed, just drop duplicates
group_cols = ['School ID', 'name', 'type', 'size', 'budget',
              'Average Math Score', 'Average Reading Score',
              'Number Passing Math', 'Number Passing Reading']

result = df_all[group_cols].drop_duplicates().reset_index(drop=True)

# Ensure correct dtypes as per target schema
result['School ID'] = result['School ID'].astype('Int64')
result['size'] = result['size'].astype('Int64')
result['budget'] = result['budget'].astype('Int64')
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)
result['Number Passing Math'] = result['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = result['Number Passing Reading'].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)