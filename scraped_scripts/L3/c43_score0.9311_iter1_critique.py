import pandas as pd

# Read source tables
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_43/training_0.csv", index_col=0)
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_43/training_1.csv", index_col=0)

# Join students with schools on school_name to get 'type' and other school info for each student
df_joined = pd.merge(df_students, df_schools[['school_name', 'type', 'size', 'budget']], on='school_name', how='inner')

# Group by 'type' and aggregate as required
result = df_joined.groupby('type').agg(
    **{
        'Total Students': ('Student ID', 'count'),
        'Total School Budget': ('budget', 'sum'),
        'Average Math Score': ('math_score', 'mean'),
        'Average Reading Score': ('reading_score', 'mean'),
        'School Size': ('size', 'mean')
    }
).reset_index()

# Write output with exact target column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_43/target_multisource_mcts.csv", index=False)