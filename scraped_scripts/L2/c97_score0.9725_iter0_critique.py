import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(df_students, df_schools, on='school_name', how='inner')

# Group by school_name and type, aggregate average scores
agg = merged.groupby(['school_name', 'type'], as_index=False).agg(
    **{
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'Total Students': ('size', 'first'),  # size is unique per school, take first
        'Total School Budget': ('budget', 'first')  # budget is unique per school, take first
    }
)

# Ensure correct types
agg['Total Students'] = agg['Total Students'].astype(int)
agg['Total School Budget'] = agg['Total School Budget'].astype(int)
agg['Average Math Score'] = agg['Average Math Score'].astype(float)
agg['Average Reading Score'] = agg['Average Reading Score'].astype(float)

# Reorder columns to match target schema
result = agg[['school_name', 'type', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_97/target_multisource_mcts.csv", index=False)