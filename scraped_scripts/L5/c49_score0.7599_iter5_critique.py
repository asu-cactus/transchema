import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_49/training_4.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Map 'Sex' to integer as per source data
df_all['Sex'] = df_all['Sex'].map({'Female': 0, 'Male': 1}).fillna(df_all['Sex'])
df_all['Sex'] = pd.to_numeric(df_all['Sex'], errors='coerce').fillna(0).astype(int)

# Group by 'Age Group' only, aggregate sums of all other columns
agg_df = df_all.groupby('Age Group', dropna=False).agg({
    'Sex': 'sum',
    "Don't know/Refused/Missing": 'sum',
    'Normal Weight': 'sum',
    'Obese': 'sum',
    'Overweight': 'sum',
    'Underweight': 'sum'
}).reset_index()

# Cast all columns except 'Age Group' to int
agg_df = agg_df.astype({
    'Sex': int,
    "Don't know/Refused/Missing": int,
    'Normal Weight': int,
    'Obese': int,
    'Overweight': int,
    'Underweight': int
})

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_49/target_multisource_mcts.csv", index=False)