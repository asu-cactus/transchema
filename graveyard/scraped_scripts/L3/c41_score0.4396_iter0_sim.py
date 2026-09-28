import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_1.csv", index_col=0)

agg_source1 = source1.groupby('school_name').agg(
    Total_Students=('Student ID', 'count'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

merged = pd.merge(source0, agg_source1, on='school_name', how='inner')

final = pd.DataFrame({
    'Total Students': [merged['Total_Students'].sum()],
    'Total School Budget': [merged['budget'].sum()],
    'Average Math Score': [merged['Average_Math_Score'].mean()],
    'Average Reading Score': [merged['Average_Reading_Score'].mean()]
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_41/target_multisource_mcts.csv", index=False)