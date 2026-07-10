import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_43/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_43/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_43/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join students with schools on school_name
merged = pd.merge(df1, df0, on='school_name', how='inner')

# Group by 'type' and aggregate as required
agg_final = merged.groupby('type').agg({
    'Student ID': 'count',          # Total Students
    'budget': 'sum',                # Total School Budget
    'math_score': 'mean',           # Average Math Score
    'reading_score': 'mean',        # Average Reading Score
    'size': 'sum'                   # School Size
}).reset_index()

# Rename columns to match target schema
agg_final = agg_final.rename(columns={
    'Student ID': 'Total Students',
    'budget': 'Total School Budget',
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score',
    'size': 'School Size'
})

# Ensure correct types
agg_final['type'] = agg_final['type'].astype(str)
agg_final['Total Students'] = agg_final['Total Students'].astype(float)
agg_final['Total School Budget'] = agg_final['Total School Budget'].astype(float)
agg_final['Average Math Score'] = agg_final['Average Math Score'].astype(float)
agg_final['Average Reading Score'] = agg_final['Average Reading Score'].astype(float)
agg_final['School Size'] = agg_final['School Size'].astype(float)

agg_final.to_csv(target_path, index=False)