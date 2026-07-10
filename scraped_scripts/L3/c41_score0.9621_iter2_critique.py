import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="school_name")

agg = merged.groupby("School ID").agg({
    'size': 'first',
    'budget': 'first',
    'math_score': 'mean',
    'reading_score': 'mean'
}).rename(columns={
    'size': 'Total Students',
    'budget': 'Total School Budget',
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
}).reset_index(drop=True)

agg['Total Students'] = agg['Total Students'].astype(int)
agg['Total School Budget'] = agg['Total School Budget'].astype(int)
agg['Average Math Score'] = agg['Average Math Score'].astype(float)
agg['Average Reading Score'] = agg['Average Reading Score'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_41/target_multisource_mcts.csv", index=False)