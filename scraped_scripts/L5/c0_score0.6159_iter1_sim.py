import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_0/training_1.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=['student_name', 'gender', 'grade', 'school_name'], 
                       value_vars=['reading_score', 'math_score'], 
                       var_name='subject', value_name='score')

df_merged = pd.merge(df1_unpivot, df0, left_on='school_name', right_on='school_name', how='inner')

df_merged['School Type'] = df_merged['type'].map({'District':1, 'Charter':1}).fillna(1).astype(int)

agg = df_merged.groupby(['school_name', 'School Type', 'size', 'budget', 'student_name', 'gender', 'grade', 'subject']).agg(
    Total_Students=('student_name', 'count'),
    Average_Score=('score', 'mean')
).reset_index()

pivot = agg.pivot_table(index=['school_name', 'School Type', 'size', 'budget', 'student_name', 'gender', 'grade'],
                        columns='subject', values='Average_Score').reset_index()

pivot.rename(columns={
    'school_name': 'School Name',
    'size': 'size',
    'budget': 'Total Budget',
    'student_name': 'student_name',
    'gender': 'gender',
    'grade': 'grade',
    'reading_score': 'Average Reading Score',
    'math_score': 'Average Math Score'
}, inplace=True)

pivot['Total Students'] = agg.groupby(['school_name', 'School Type', 'size', 'budget', 'student_name', 'gender', 'grade'])['Total_Students'].first().values

pivot['School ID'] = 0
pivot['Total Passing Math'] = 0
pivot['Total Passing Reading'] = 0

final_cols = ['School Name', 'School Type', 'Total Students', 'student_name', 'gender', 'grade',
              'Average Reading Score', 'Average Math Score', 'School ID', 'size', 'Total Budget',
              'Total Passing Math', 'Total Passing Reading']

pivot = pivot[final_cols]

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length5_0/target_multisource_mcts.csv", index=False)