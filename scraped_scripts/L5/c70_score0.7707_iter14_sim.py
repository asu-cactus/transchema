import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)

def category_to_int(cat_series):
    unique_cats = cat_series.dropna().unique()
    cat_map = {cat: i+1 for i, cat in enumerate(sorted(unique_cats))}
    return cat_series.map(cat_map), cat_map

df['Category'], _ = category_to_int(df['Category'])

df['Winner'] = df['Winner'].map({'YES': 1}).fillna(0).astype(int)

df['Movie'] = df['Movie'].str.len()
df['Movie'] = df['Movie'].apply(lambda x: 1 if x > 0 else 0)

df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)