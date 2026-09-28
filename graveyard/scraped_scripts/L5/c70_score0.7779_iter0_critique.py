import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Year'] = df['Year'].str.extract(r'(\d+)').astype(int)
    dfs.append(df)

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Encode 'Category' and 'Movie' globally after union
df_all['Category'] = df_all['Category'].astype('category').cat.codes + 1
df_all['Movie'] = df_all['Movie'].astype('category').cat.codes + 1

# Map 'Winner' to int
df_all['Winner'] = df_all['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

# GROUP BY 'Nominee' and 'Year', aggregate others by max
result = df_all.groupby(['Nominee', 'Year'], as_index=False).agg({
    'Category': 'max',
    'Movie': 'max',
    'Winner': 'max'
})

# Reorder columns to match target schema
result = result[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)