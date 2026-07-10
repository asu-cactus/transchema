import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

# Join on 'school_name'
merged = pd.merge(df0, df1, on='school_name', how='inner')

# Group by 'School ID' and 'size' (School Size)
agg = merged.groupby(['School ID', 'size']).agg(
    Total_Students=('Student ID', 'count'),
    Total_School_Budget=('budget', 'sum'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

# Rename columns to match target schema
agg = agg.rename(columns={
    'size': 'School Size',
    'Total_Students': 'Total Students',
    'Total_School_Budget': 'Total School Budget',
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score'
})

# Select only the target columns in order
final = agg[['School Size', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

# Ensure correct types
final = final.astype({
    'School Size': int,
    'Total Students': int,
    'Total School Budget': int,
    'Average Math Score': float,
    'Average Reading Score': float
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv", index=False)