import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert Year to integer by extracting digits
df_all['Year'] = df_all['Year'].str.extract(r'(\d+)').astype(int)

# Convert Category to categorical codes starting from 1
df_all['Category'] = df_all['Category'].astype('category').cat.codes + 1

# Extract Movie name before '{' and strip spaces, then convert to categorical codes starting from 1
df_all['Movie'] = df_all['Movie'].str.extract(r'^([^{}]+)').iloc[:, 0].str.strip()
df_all['Movie'] = df_all['Movie'].astype('category').cat.codes + 1

# Map Winner to int (YES=1, NO=0), fill missing with 0
df_all['Winner'] = df_all['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

# Group by Nominee and take first occurrence of other columns to ensure unique Nominee rows
df_final = df_all.groupby('Nominee', dropna=False).agg({
    'Year': 'first',
    'Category': 'first',
    'Movie': 'first',
    'Winner': 'first'
}).reset_index()

# Ensure correct dtypes
df_final = df_final.astype({
    'Nominee': str,
    'Year': int,
    'Category': int,
    'Movie': int,
    'Winner': int
})

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)