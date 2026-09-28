import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_1.csv", index_col=0)

agg = df_students.groupby('school_name').agg(
    Total_Students=('Student ID', 'count'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

merged = pd.merge(agg, df_schools, on='school_name', how='inner')

merged = merged.rename(columns={
    'size': 'Total Students',
    'budget': 'Total School Budget',
    'Total_Students': 'Total Students',
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score'
})

result = merged[['school_name', 'type', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

result['Total Students'] = result['Total Students'].astype(int)
result['Total School Budget'] = result['Total School Budget'].astype(int)
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_97/target_multisource_mcts.csv", index=False)