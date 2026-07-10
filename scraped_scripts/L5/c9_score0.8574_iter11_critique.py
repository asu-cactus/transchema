import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Nominee as string
df['Nominee'] = df['Nominee'].astype(str)

# Extract year number from 'Year' string and convert to int
df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)

# Convert 'Category' to categorical codes starting from 1
df['Category'] = df['Category'].astype('category').cat.codes + 1

# Convert 'Movie' to categorical codes starting from 1
df['Movie'] = df['Movie'].astype('category').cat.codes + 1

# Map 'Winner' to 1/0
df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

# Group by 'Nominee' and aggregate other columns by max
df = df.groupby('Nominee', as_index=False).agg({
    'Year': 'max',
    'Category': 'max',
    'Movie': 'max',
    'Winner': 'max'
})

# Reorder columns to match target schema
df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)