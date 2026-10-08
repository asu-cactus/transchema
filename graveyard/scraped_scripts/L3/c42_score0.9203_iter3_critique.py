import pandas as pd

# Read sources with index_col=0 as instructed
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_42/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(source0, source1, on='school_name', how='inner')

# Group by school_name (unique key for schools)
agg = merged.groupby('school_name').agg(
    School_Size=('size', 'sum'),
    Total_Students=('Student ID', 'count'),
    Total_School_Budget=('budget', 'sum'),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean')
).reset_index()

# The target schema does not include school_name, so drop it
result = agg[['School_Size', 'Total_Students', 'Total_School_Budget', 'Average_Math_Score', 'Average_Reading_Score']]

# Cast types as per target schema
result['School_Size'] = result['School_Size'].astype(int)
result['Total_Students'] = result['Total_Students'].astype(int)
result['Total_School_Budget'] = result['Total_School_Budget'].astype(int)
result['Average_Math_Score'] = result['Average_Math_Score'].astype(float)
result['Average_Reading_Score'] = result['Average_Reading_Score'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_42/target_multisource_mcts.csv", index=False)