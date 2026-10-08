import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

agg0 = df0.groupby('size').agg({'size':'sum', 'budget':'sum'}).rename(columns={'size':'School Size', 'budget':'Total School Budget'}).reset_index(drop=True)
agg0['School Size'] = agg0.index

agg1 = df1.groupby('school_name').agg(
    Total_Students=('student_name', 'count'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

df0_renamed = df0.rename(columns={'size':'School Size', 'school_name':'school_name'})

merged = pd.merge(df0_renamed, agg1, on='school_name', how='inner')

final = merged.groupby('School Size').agg(
    Total_Students=('Total_Students', 'sum'),
    Total_School_Budget=('budget', 'sum'),
    Average_Math_Score=('Average_Math_Score', 'mean'),
    Average_Reading_Score=('Average_Reading_Score', 'mean')
).reset_index()

final = final.astype({
    'School Size': int,
    'Total_Students': int,
    'Total_School_Budget': int,
    'Average_Math_Score': float,
    'Average_Reading_Score': float
})

final = final.rename(columns={
    'Total_Students': 'Total Students',
    'Total_School_Budget': 'Total School Budget',
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score'
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv", index=False)