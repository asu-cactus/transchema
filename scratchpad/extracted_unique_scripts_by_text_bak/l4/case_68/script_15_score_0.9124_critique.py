import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_68/training_1.csv", index_col=0)

# Join on school_name
df_join = pd.merge(df0, df1, on='school_name', how='inner')

# Group by school_name and type (which corresponds to 'a' in target)
df_agg = df_join.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'sum',
    'budget': 'sum',
    'reading_score': 'mean',
    'math_score': 'mean'
})

# Rename columns to match target schema
df_agg = df_agg.rename(columns={
    'type': 'a',
    'size': 'b',
    'budget': 'c',
    'reading_score': 'd',
    'math_score': 'e'
})

# Ensure correct types
df_agg['b'] = df_agg['b'].astype(int)
df_agg['c'] = df_agg['c'].astype(int)
df_agg['d'] = df_agg['d'].astype(float)
df_agg['e'] = df_agg['e'].astype(float)

# Reorder columns as per target schema
df_agg = df_agg[['school_name', 'a', 'b', 'c', 'd', 'e']]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_68/target_multisource_mcts.csv", index=False)