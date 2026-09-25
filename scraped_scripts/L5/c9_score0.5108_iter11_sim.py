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

df['Nominee'] = df['Nominee'].astype(str)

df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)

df['Category'] = df['Category'].astype('category').cat.codes + 1

def extract_first_int(x):
    if pd.isna(x):
        return pd.NA
    s = str(x)
    import re
    m = re.search(r'\d+', s)
    if m:
        return int(m.group())
    else:
        return pd.NA

df['Movie'] = df['Movie'].apply(extract_first_int)
df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

df = df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)