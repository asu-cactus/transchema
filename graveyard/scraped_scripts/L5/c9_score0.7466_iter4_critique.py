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
    df['Year'] = df['Year'].str.extract(r'(\d+)').astype(int)
    df['Category'] = df['Category'].astype('category').cat.codes + 1
    df['Movie'] = df['Movie'].str.extract(r"\{\'(.+?)\'\}").fillna(df['Movie'])
    df['Movie'] = df['Movie'].astype('category').cat.codes + 1
    df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)

result = result[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

# Remove duplicates to match target unique tuples
result = result.drop_duplicates(subset=['Nominee', 'Year', 'Category', 'Movie', 'Winner'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)