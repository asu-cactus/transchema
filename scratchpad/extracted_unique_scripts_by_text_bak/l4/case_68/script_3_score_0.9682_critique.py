import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema
df0_renamed = df0.rename(columns={'type': 'a', 'size': 'b', 'budget': 'c'})

# Aggregate df1 by school_name to get mean reading_score and math_score
agg_scores = df1.groupby('school_name').agg({'reading_score': 'mean', 'math_score': 'mean'}).reset_index()
agg_scores = agg_scores.rename(columns={'reading_score': 'd', 'math_score': 'e'})

# Join df0 and aggregated df1 on school_name
result = pd.merge(df0_renamed[['school_name', 'a', 'b', 'c']], agg_scores, on='school_name', how='inner')

# Ensure correct column order
result = result[['school_name', 'a', 'b', 'c', 'd', 'e']]

# Cast types to match target schema
result['b'] = result['b'].astype(int)
result['c'] = result['c'].astype(int)
result['d'] = result['d'].astype(float)
result['e'] = result['e'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)