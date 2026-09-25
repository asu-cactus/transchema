import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_41/training_1.csv", index_col=0)

grouped = source1.groupby('school_name').agg(
    Total_Students=('Student ID', 'count'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

merged = pd.merge(source0, grouped, on='school_name', how='inner')

result = merged.groupby('type').agg(
    Total_Students=('Total_Students', 'sum'),
    Total_School_Budget=('budget', 'sum'),
    Average_Math_Score=('Average_Math_Score', 'mean'),
    Average_Reading_Score=('Average_Reading_Score', 'mean')
).reset_index()

final = result[['Total_Students', 'Total_School_Budget', 'Average_Math_Score', 'Average_Reading_Score']]

final['Total_Students'] = final['Total_Students'].astype(int)
final['Total_School_Budget'] = final['Total_School_Budget'].astype(int)
final['Average_Math_Score'] = final['Average_Math_Score'].astype(float)
final['Average_Reading_Score'] = final['Average_Reading_Score'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_41/target_multisource_mcts.csv", index=False)