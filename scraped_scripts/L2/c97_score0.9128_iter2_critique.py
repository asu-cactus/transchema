import pandas as pd

df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_0.csv", index_col=0)
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_97/training_1.csv", index_col=0)

# Join on school_name
df_joined = pd.merge(df_students, df_schools, on='school_name', how='inner')

# Group by school_name and type, aggregate as required
df_final = df_joined.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'sum',          # Total Students
    'budget': 'sum',        # Total School Budget
    'math_score': 'mean',   # Average Math Score
    'reading_score': 'mean' # Average Reading Score
})

# Rename columns to match target schema
df_final = df_final.rename(columns={
    'size': 'Total Students',
    'budget': 'Total School Budget',
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length2_97/target_multisource_mcts.csv", index=False)