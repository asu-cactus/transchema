import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_1.csv", index_col=0)

agg0 = source0.groupby('type').agg({'size':'sum', 'budget':'sum'}).reset_index()
agg1 = source1.groupby('school_name').agg({'math_score':'mean', 'reading_score':'mean'}).reset_index()

merged = pd.merge(agg0, source0[['school_name', 'type']], on='type', how='left').drop_duplicates(subset=['school_name', 'type'])
merged_scores = pd.merge(merged, agg1, on='school_name', how='inner')

result = merged_scores.groupby('type').agg({
    'size':'sum',
    'budget':'sum',
    'math_score':'mean',
    'reading_score':'mean'
}).reset_index()

result = result.rename(columns={
    'size': 'Total Students',
    'budget': 'Total School Budget',
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
})

result['Total Students'] = result['Total Students'].astype(int)
result['Total School Budget'] = result['Total School Budget'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_41/target_multisource_mcts.csv", index=False)