import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_1.csv", index_col=0)

df0_selected = df0[['school_name', 'reading_score', 'math_score', 'Student ID']]

df_merged = pd.merge(df0_selected, df1[['school_name', 'type', 'size', 'budget']], on='school_name', how='inner')

result = df_merged.groupby(['school_name', 'type'], as_index=False).agg(
    Total_Students=('Student ID', 'count'),
    Total_School_Budget=('budget', 'sum'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
)

result = result.rename(columns={
    'Total_Students': 'Total Students',
    'Total_School_Budget': 'Total School Budget',
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score'
})

result['Total Students'] = result['Total Students'].astype(int)
result['Total School Budget'] = result['Total School Budget'].astype(int)
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_97/target_multisource_mcts.csv", index=False)