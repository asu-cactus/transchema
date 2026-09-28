import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(df0, df1, on='school_name', how='inner')

# Group by school_name and type (which corresponds to target columns school_name and a)
agg = merged.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'sum',
    'budget': 'sum',
    'reading_score': 'mean',
    'math_score': 'mean'
})

# Rename columns to match target schema
agg = agg.rename(columns={
    'type': 'a',
    'size': 'b',
    'budget': 'c',
    'reading_score': 'd',
    'math_score': 'e'
})

# Ensure integer columns are int type
agg['b'] = agg['b'].astype(int)
agg['c'] = agg['c'].astype(int)

# Reorder columns to match target schema
result = agg[['school_name', 'a', 'b', 'c', 'd', 'e']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)