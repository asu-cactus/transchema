import pandas as pd
import numpy as np

source0_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df_join = pd.merge(df0, df1, left_on="school_name", right_on="school_name", how="inner")

df_join['passing_math'] = (df_join['math_score'] >= 70).astype(int)
df_join['passing_reading'] = (df_join['reading_score'] >= 70).astype(int)

agg = df_join.groupby(
    ['school_name', 'type', 'School ID', 'size', 'budget'],
    as_index=False
).agg(
    Total_Students=('student_name', 'count'),
    Average_Reading_Score=('reading_score', 'mean'),
    Average_Math_Score=('math_score', 'mean'),
    Total_Passing_Math=('passing_math', 'sum'),
    Total_Passing_Reading=('passing_reading', 'sum')
)

agg.rename(columns={
    'school_name': 'School Name',
    'type': 'School Type',
    'size': 'size',
    'budget': 'Total Budget',
    'School ID': 'School ID',
    'Total_Students': 'Total Students',
    'Average_Reading_Score': 'Average Reading Score',
    'Average_Math_Score': 'Average Math Score',
    'Total_Passing_Math': 'Total Passing Math',
    'Total_Passing_Reading': 'Total Passing Reading'
}, inplace=True)

agg['student_name'] = 1
agg['gender'] = 1
agg['grade'] = 1

agg['School Name'] = agg['School Name'].astype(str)
agg['School Type'] = agg['School Type'].apply(lambda x: 1 if str(x).lower() == 'district' else 0).astype(int)
agg['Total Students'] = agg['Total Students'].astype(int)
agg['student_name'] = agg['student_name'].astype(int)
agg['gender'] = agg['gender'].astype(int)
agg['grade'] = agg['grade'].astype(int)
agg['Average Reading Score'] = agg['Average Reading Score'].round().astype(int)
agg['Average Math Score'] = agg['Average Math Score'].round().astype(int)
agg['School ID'] = agg['School ID'].astype(int)
agg['size'] = agg['size'].astype(int)
agg['Total Budget'] = agg['Total Budget'].astype(int)
agg['Total Passing Math'] = agg['Total Passing Math'].astype(int)
agg['Total Passing Reading'] = agg['Total Passing Reading'].astype(int)

agg = agg[['School Name', 'School Type', 'Total Students', 'student_name', 'gender', 'grade',
           'Average Reading Score', 'Average Math Score', 'School ID', 'size', 'Total Budget',
           'Total Passing Math', 'Total Passing Reading']]

agg.to_csv(target_path, index=False)