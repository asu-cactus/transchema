import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

# Join Source4_77_1 and Source4_77_2 on school name
df_school = pd.merge(df1, df2, left_on='name', right_on='school', how='inner')

# Join the above with student data (df0) on school name
df_all = pd.merge(df_school, df0, left_on='name', right_on='school', how='inner')

# Group by school-level keys to aggregate student scores
result = df_all.groupby(['School ID', 'name', 'type', 'size', 'budget'], as_index=False).agg(
    **{
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'Number Passing Math': ('math_score', lambda x: (x >= 60).sum()),
        'Number Passing Reading': ('reading_score', lambda x: (x >= 60).sum())
    }
)

# Ensure integer columns have correct dtype
result['School ID'] = result['School ID'].astype('Int64')
result['size'] = result['size'].astype('Int64')
result['budget'] = result['budget'].astype('Int64')
result['Number Passing Math'] = result['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = result['Number Passing Reading'].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)