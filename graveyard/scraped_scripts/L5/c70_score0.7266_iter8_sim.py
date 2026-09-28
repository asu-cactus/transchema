import pandas as pd

def load_and_prepare_source(path):
    df = pd.read_csv(path, index_col=0)
    df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
    df['Category'] = df['Category'].astype('category').cat.codes + 1
    df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)
    df['Movie'] = 1
    return df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_70/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_70/training_4.csv"
]

dfs = [load_and_prepare_source(p) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby(['Nominee', 'Year', 'Category'], as_index=False).agg({'Movie':'count', 'Winner':'sum'})

agg = agg.rename(columns={'Movie': 'Movie', 'Winner': 'Winner'})

agg['Category'] = agg['Category'].astype(int)
agg['Year'] = agg['Year'].astype(int)
agg['Movie'] = agg['Movie'].astype(int)
agg['Winner'] = agg['Winner'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_70/target_multisource_mcts.csv", index=False)