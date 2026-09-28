import pandas as pd
import numpy as np

source0_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df1['passing_reading'] = (df1['reading_score'] >= 70).astype(int)
df1['passing_math'] = (df1['math_score'] >= 70).astype(int)

agg = df1.groupby(['school_name', 'gender', 'grade']).agg(
    Total_Students=('student_name', 'count'),
    Average_Reading_Score=('reading_score', 'mean'),
    Average_Math_Score=('math_score', 'mean'),
    Total_Passing_Reading=('passing_reading', 'sum'),
    Total_Passing_Math=('passing_math', 'sum')
).reset_index()

merged = pd.merge(agg, df0, left_on='school_name', right_on='school_name', how='inner')

# Map 'type' to integer: District=1, Charter=2 (based on examples and target schema expecting integer)
type_map = {'District': 1, 'Charter': 2}
merged['School Type'] = merged['type'].map(type_map).fillna(0).astype(int)

# Rename columns and select final columns as per target schema
result = pd.DataFrame()
result['School Name'] = merged['school_name']
result['School Type'] = merged['School Type']
result['Total Students'] = merged['Total_Students']
# 'student_name', 'gender', 'grade' columns in target are integers, so encode them as categorical codes
result['student_name'] = merged['Total_Students']  # The target example shows 'student_name' as integer 1, likely count or presence; use Total Students as proxy
result['gender'] = merged['gender'].astype('category').cat.codes + 1  # +1 to match example (F=1, M=0 -> 1,0 +1 = 1,2)
result['grade'] = merged['grade'].astype('category').cat.codes + 1

result['Average Reading Score'] = merged['Average_Reading_Score'].round().astype(int)
result['Average Math Score'] = merged['Average_Math_Score'].round().astype(int)
result['School ID'] = merged['School ID'].astype(int)
result['size'] = merged['size'].astype(int)
result['Total Budget'] = merged['budget'].astype(int)
result['Total Passing Math'] = merged['Total_Passing_Math'].astype(int)
result['Total Passing Reading'] = merged['Total_Passing_Reading'].astype(int)

result.to_csv(target_path, index=False)