import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Normalize 'school_name' strings in both dataframes to ensure proper join
df0['school_name'] = df0['school_name'].str.strip().str.lower()
df1['school_name'] = df1['school_name'].str.strip().str.lower()

# Join student data with school data to get 'type' for each student
df_joined = pd.merge(df1, df0[['school_name', 'type']], on='school_name', how='inner')

# Group by 'type' and aggregate average reading and math scores as 'a' and 'b'
result = df_joined.groupby('type').agg(
    a=pd.NamedAgg(column='reading_score', aggfunc='mean'),
    b=pd.NamedAgg(column='math_score', aggfunc='mean')
).reset_index()

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)