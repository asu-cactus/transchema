import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

agg_df0 = df0.groupby('school').agg(
    **{
        'Average Reading Score': ('reading_score', 'mean'),
        'Average Math Score': ('math_score', 'mean'),
        'Number Passing Reading': (lambda x: (x >= 70).sum(), 'reading_score'),
        'Number Passing Math': (lambda x: (x >= 70).sum(), 'math_score'),
    }
).reset_index()

agg_df0.rename(columns={'school': 'name'}, inplace=True)

merged_1 = pd.merge(agg_df0, df1, left_on='name', right_on='name', how='inner')

merged_2 = pd.merge(merged_1, df2, left_on='name', right_on='school', how='inner')

result = merged_2.rename(columns={'school': 'name'})

result = result[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score', 'Number Passing Math', 'Number Passing Reading']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)