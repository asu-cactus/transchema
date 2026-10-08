import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Extract integer year from 'Year' string
df['Year'] = df['Year'].str.extract(r'(\d+)').astype(int)

# Encode 'Category' as categorical codes starting from 1
df['Category'] = df['Category'].astype('category').cat.codes + 1

# Encode 'Movie' as categorical codes starting from 1
df['Movie'] = df['Movie'].astype('category').cat.codes + 1

# Map 'Winner' from YES/NO to 1/0
df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

# Keep only relevant columns in target order
df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

# Group by 'Nominee' and aggregate other columns by max to remove duplicates
df = df.groupby('Nominee', as_index=False).agg({
    'Year': 'max',
    'Category': 'max',
    'Movie': 'max',
    'Winner': 'max'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)