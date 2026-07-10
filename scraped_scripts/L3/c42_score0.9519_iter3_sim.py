import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

agg = source1.groupby(['gender', 'grade', 'school_name']).agg(
    Total_Students=('Student ID', 'count'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

agg2 = agg.groupby('school_name').agg(
    Total_Students=('Total_Students', 'sum'),
    Average_Math_Score=('Average_Math_Score', 'mean'),
    Average_Reading_Score=('Average_Reading_Score', 'mean')
).reset_index()

source0_agg = source0.groupby(['type', 'school_name']).agg(
    School_Size=('size', 'sum'),
    Total_School_Budget=('budget', 'sum')
).reset_index()

merged = pd.merge(source0_agg, agg2, on='school_name', how='inner')

result = merged[['School_Size', 'Total_Students', 'Total_School_Budget', 'Average_Math_Score', 'Average_Reading_Score']]

result['School_Size'] = result['School_Size'].astype(int)
result['Total_Students'] = result['Total_Students'].astype(int)
result['Total_School_Budget'] = result['Total_School_Budget'].astype(int)
result['Average_Math_Score'] = result['Average_Math_Score'].astype(float)
result['Average_Reading_Score'] = result['Average_Reading_Score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv", index=False)