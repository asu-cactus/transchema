import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_68/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_68/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_68/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on school_name
df_joined = pd.merge(df0, df1, on='school_name', how='inner')

# Group by school_name and type, aggregate as required
df_grouped = df_joined.groupby(['school_name', 'type'], as_index=False).agg({
    'size': 'sum',
    'budget': 'sum',
    'math_score': 'mean',
    'reading_score': 'mean'
})

# Rename columns to match target schema
df_grouped.rename(columns={
    'size': 'Total Students',
    'budget': 'Total School Budget',
    'math_score': 'Average Math Score',
    'reading_score': 'Average Reading Score'
}, inplace=True)

# Reorder columns as per target schema
df_grouped = df_grouped[['school_name', 'type', 'Total Students', 'Total School Budget', 'Average Math Score', 'Average Reading Score']]

df_grouped.to_csv(target_path, index=False)