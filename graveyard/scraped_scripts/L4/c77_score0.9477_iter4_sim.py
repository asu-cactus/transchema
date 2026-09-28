import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

df0['passing_math'] = (df0['math_score'] >= 60).astype(int)
df0['passing_reading'] = (df0['reading_score'] >= 60).astype(int)

agg = df0.groupby(['school', 'gender', 'grade']).agg(
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean'),
    Number_Students=('Student ID', 'count'),
    Number_Passing_Math=('passing_math', 'sum'),
    Number_Passing_Reading=('passing_reading', 'sum')
).reset_index()

# Join agg with df1 on school name and type
# df1 has columns: School ID, name, type, size, budget
# agg has school, gender, grade, and aggregated scores
# The target schema is per school, so we need to aggregate agg further by school to get per school values

agg_school = agg.groupby('school').agg(
    Average_Math_Score=('Average_Math_Score', 'mean'),
    Average_Reading_Score=('Average_Reading_Score', 'mean'),
    Number_Passing_Math=('Number_Passing_Math', 'sum'),
    Number_Passing_Reading=('Number_Passing_Reading', 'sum')
).reset_index()

# Join agg_school with df1 on school name = name
merged = pd.merge(df1, agg_school, left_on='name', right_on='school', how='inner')

# Select and rename columns to match target schema
result = merged.rename(columns={
    'School ID': 'School ID',
    'name': 'name',
    'type': 'type',
    'size': 'size',
    'budget': 'budget',
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score',
    'Number_Passing_Math': 'Number Passing Math',
    'Number_Passing_Reading': 'Number Passing Reading'
})

result = result[['School ID', 'name', 'type', 'size', 'budget', 'Average Math Score', 'Average Reading Score', 'Number Passing Math', 'Number Passing Reading']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)