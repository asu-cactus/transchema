import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)

agg_df0 = df0.groupby('school').agg(
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

# Source2 already has aggregated columns but we must ensure column names match target schema
# Rename columns in df2 to match target schema except 'school' which will be used for join
df2_renamed = df2.rename(columns={
    'school': 'school',
    'Average Math Score': 'Average_Math_Score_2',
    'Average Reading Score': 'Average_Reading_Score_2',
    'Number Passing Math': 'Number_Passing_Math',
    'Number Passing Reading': 'Number_Passing_Reading'
})

# Join df1 and df2 on school name (df1.name == df2.school)
join_1 = pd.merge(df1, df2_renamed, left_on='name', right_on='school', how='inner')

# Join the above result with aggregated df0 on school name (join_1.name == agg_df0.school)
final_join = pd.merge(join_1, agg_df0, left_on='name', right_on='school', how='inner')

# Compose final dataframe with correct columns and types
result = pd.DataFrame()
result['School ID'] = final_join['School ID'].astype(int)
result['name'] = final_join['name']
result['type'] = final_join['type']
result['size'] = final_join['size'].astype(int)
result['budget'] = final_join['budget'].astype(int)
# Use Average Math and Reading Scores from df2 (aggregated source2) as they match target examples better
result['Average Math Score'] = final_join['Average_Math_Score_2'].astype(float)
result['Average Reading Score'] = final_join['Average_Reading_Score_2'].astype(float)
result['Number Passing Math'] = final_join['Number_Passing_Math'].astype(int)
result['Number Passing Reading'] = final_join['Number_Passing_Reading'].astype(int)

result.to_csv(output_path, index=False)