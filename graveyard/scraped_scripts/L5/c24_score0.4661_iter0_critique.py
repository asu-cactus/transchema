import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_24/training_1.csv", index_col=0)

# Join on school_name
merged = pd.merge(df0, df1[['school_name', 'budget']], on='school_name', how='inner')

# Group by school_name and Student ID, aggregate scores by mean, budget by first (budget is constant per school)
agg = merged.groupby(['school_name', 'Student ID']).agg({
    'math_score': 'mean',
    'reading_score': 'mean',
    'budget': 'first'
}).reset_index()

# Cast columns to correct types
agg['school_name'] = agg['school_name'].astype(str)
agg['Student ID'] = agg['Student ID'].astype(int)
agg['budget'] = agg['budget'].astype(int)
agg['math_score'] = agg['math_score'].astype(float)
agg['reading_score'] = agg['reading_score'].astype(float)

# Reorder columns as per target schema
agg = agg[['school_name', 'Student ID', 'budget', 'math_score', 'reading_score']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_24/target_multisource_mcts.csv", index=False)