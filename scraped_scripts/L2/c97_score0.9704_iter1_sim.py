import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_1.csv", index_col=0)

pivot = df_students.pivot_table(index='school_name', columns='gender', values=['reading_score', 'math_score'], aggfunc='mean')
pivot.columns = ['Average Reading Score F', 'Average Reading Score M', 'Average Math Score F', 'Average Math Score M']
pivot = pivot.reset_index()

pivot['Average Reading Score'] = pivot[['Average Reading Score F', 'Average Reading Score M']].mean(axis=1)
pivot['Average Math Score'] = pivot[['Average Math Score F', 'Average Math Score M']].mean(axis=1)

agg_students = df_students.groupby('school_name').agg({'student_name':'count'}).rename(columns={'student_name':'Total Students'}).reset_index()

merged = pivot.merge(agg_students, on='school_name', how='left')
merged = merged.merge(df_schools[['school_name', 'type', 'size', 'budget']], on='school_name', how='left')

result = merged.rename(columns={'size':'Total Students', 'budget':'Total School Budget'})
result['Total Students'] = result['Total Students'].fillna(merged['Total Students'])
result = result[['school_name', 'type', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

result['Total Students'] = result['Total Students'].astype('Int64')
result['Total School Budget'] = result['Total School Budget'].astype('Int64')
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_97/target_multisource_mcts.csv", index=False)