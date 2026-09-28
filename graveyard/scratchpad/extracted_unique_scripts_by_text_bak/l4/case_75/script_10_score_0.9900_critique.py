import pandas as pd

# Read sources
df_schools = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
df_students = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Join on school_name to get 'type' for each student
df_joined = pd.merge(df_students, df_schools[['school_name', 'type']], on='school_name', how='inner')

# Group by 'type' and aggregate mean reading and math scores
df_result = df_joined.groupby('type', as_index=False).agg({
    'reading_score': 'mean',
    'math_score': 'mean'
})

# Rename columns to match target schema
df_result.rename(columns={'reading_score': 'a', 'math_score': 'b'}, inplace=True)

# Ensure correct dtypes
df_result['a'] = df_result['a'].astype(float)
df_result['b'] = df_result['b'].astype(float)
df_result['type'] = df_result['type'].astype(str)

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)