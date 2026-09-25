import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_78/training_2.csv", index_col=0)

df_union = pd.concat([source0, source2.rename(columns={
    'reading_score': 'Average Reading Score',
    'math_score': 'Average Math Score',
    'school': 'school'
})], ignore_index=True, sort=False)

agg = df_union.groupby('school').agg({
    'Average Math Score': 'mean',
    'Average Reading Score': 'mean',
    'Number Passing Math': 'sum',
    'Number Passing Reading': 'sum'
}).reset_index()

df_joined = agg.merge(source1, left_on='school', right_on='name', how='inner')

result = pd.DataFrame()
result['School ID'] = df_joined['School ID'].astype('Int64')
result['name'] = df_joined['name']
result['type'] = df_joined['type']
result['size'] = df_joined['size'].astype('Int64')
result['budget'] = df_joined['budget'].astype('Int64')
result['Average Math Score'] = df_joined['Average Math Score'].astype(float)
result['Average Reading Score'] = df_joined['Average Reading Score'].astype(float)
result['Number Passing Math'] = df_joined['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = df_joined['Number Passing Reading'].astype('Int64')
result['School Size'] = df_joined['size'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_78/target_multisource_mcts.csv", index=False)