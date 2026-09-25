import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_72/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_72/training_2.csv', index_col=0)

# Join df0 and df1 on 'condition'
df01 = pd.merge(df0, df1, on='condition', how='inner', suffixes=('_0', '_1'))

# Join the result with df2 on 'condition'
df012 = pd.merge(df01, df2, on='condition', how='inner')

# Sum clicks from df0 grouped by 'condition'
result = df012.groupby('condition')['click_0'].sum().reset_index()

# Rename columns to match target schema
result.columns = ['condition', '0']

result['condition'] = result['condition'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv', index=False)