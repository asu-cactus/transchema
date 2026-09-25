import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_30/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_30/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length5_30/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on school_name
df_merged = pd.merge(df1, df0[['school_name', 'size', 'budget']], on='school_name', how='inner')

# Group by school_name, size, budget and aggregate mean scores
agg = df_merged.groupby(['school_name', 'size', 'budget'], as_index=False).agg({
    'math_score': 'mean',
    'reading_score': 'mean'
})

# Assign Student ID = size
agg['Student ID'] = agg['size']

# Compute budget = budget * size
agg['budget'] = agg['budget'] * agg['size']

# Select and reorder columns as per target schema
result = agg[['school_name', 'Student ID', 'budget', 'math_score', 'reading_score']]

# Cast types as per target schema
result['Student ID'] = result['Student ID'].astype(int)
result['budget'] = result['budget'].astype(int)
result['math_score'] = result['math_score'].astype(float)
result['reading_score'] = result['reading_score'].astype(float)

result.to_csv(output_path, index=False)