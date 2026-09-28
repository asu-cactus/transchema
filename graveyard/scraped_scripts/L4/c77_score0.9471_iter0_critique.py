import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv"

# Read sources with index_col=0 as instructed
df0 = pd.read_csv(source0_path, index_col=0)  # student-level
df1 = pd.read_csv(source1_path, index_col=0)  # school dimension
df2 = pd.read_csv(source2_path, index_col=0)  # aggregated scores by school

# Aggregate df0 by school to get average scores and counts
agg_df0 = df0.groupby('school').agg(
    Average_Math_Score_0=('math_score', 'mean'),
    Average_Reading_Score_0=('reading_score', 'mean'),
    Number_Passing_Math_0=('math_score', lambda x: (x >= 60).sum()),
    Number_Passing_Reading_0=('reading_score', lambda x: (x >= 60).sum())
).reset_index()

# Rename df2 columns to match target schema (except 'school' which is key)
df2_renamed = df2.rename(columns={
    'school': 'school',
    'Average Math Score': 'Average_Math_Score_2',
    'Average Reading Score': 'Average_Reading_Score_2',
    'Number Passing Math': 'Number_Passing_Math_2',
    'Number Passing Reading': 'Number_Passing_Reading_2'
})

# Join df1 and df2 on school name (df1.name == df2.school)
join_1 = pd.merge(df1, df2_renamed, left_on='name', right_on='school', how='inner')

# Join the above with aggregated df0 on school name (join_1.name == agg_df0.school)
join_2 = pd.merge(join_1, agg_df0, left_on='name', right_on='school', how='inner')

# Now group by School ID and name (unique keys)
# For type, size, budget take first (constant per school)
# For average scores, take mean of df2 and df0 averages
# For passing counts, sum counts from df2 and df0

result = join_2.groupby(['School ID', 'name'], as_index=False).agg({
    'type': 'first',
    'size': 'first',
    'budget': 'first',
    'Average_Math_Score_2': 'mean',
    'Average_Reading_Score_2': 'mean',
    'Average_Math_Score_0': 'mean',
    'Average_Reading_Score_0': 'mean',
    'Number_Passing_Math_2': 'sum',
    'Number_Passing_Reading_2': 'sum',
    'Number_Passing_Math_0': 'sum',
    'Number_Passing_Reading_0': 'sum'
})

# Compute final average scores as mean of the two averages (df2 and df0)
result['Average Math Score'] = (result['Average_Math_Score_2'] + result['Average_Math_Score_0']) / 2
result['Average Reading Score'] = (result['Average_Reading_Score_2'] + result['Average_Reading_Score_0']) / 2

# Compute final passing counts as sum of both sources
result['Number Passing Math'] = result['Number_Passing_Math_2'] + result['Number_Passing_Math_0']
result['Number Passing Reading'] = result['Number_Passing_Reading_2'] + result['Number_Passing_Reading_0']

# Select and reorder columns to match target schema exactly
final_result = result[[
    'School ID', 'name', 'type', 'size', 'budget',
    'Average Math Score', 'Average Reading Score',
    'Number Passing Math', 'Number Passing Reading'
]]

# Cast columns to correct types
final_result['School ID'] = final_result['School ID'].astype(int)
final_result['type'] = final_result['type'].astype(str)
final_result['size'] = final_result['size'].astype(int)
final_result['budget'] = final_result['budget'].astype(int)
final_result['Average Math Score'] = final_result['Average Math Score'].astype(float)
final_result['Average Reading Score'] = final_result['Average Reading Score'].astype(float)
final_result['Number Passing Math'] = final_result['Number Passing Math'].astype(int)
final_result['Number Passing Reading'] = final_result['Number Passing Reading'].astype(int)

# Write to output CSV
final_result.to_csv(output_path, index=False)