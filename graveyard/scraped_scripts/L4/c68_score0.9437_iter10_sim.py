import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

agg_student = df1.groupby('school_name').agg(
    c=('Student ID', 'count'),
    d=('math_score', 'mean')
).reset_index()

agg_budget = df0.groupby(['school_name', 'type']).agg(
    b=('budget', 'sum')
).reset_index()

merged = pd.merge(agg_student, agg_budget, on='school_name', how='inner')

merged['a'] = merged['type']
merged['e'] = merged['d']

result = merged[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)