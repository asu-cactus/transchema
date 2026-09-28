import pandas as pd

def load_and_prepare_source(path):
    df = pd.read_csv(path, index_col=0)
    df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
    df['Category'] = df['Category'].astype('category').cat.codes + 1
    df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)
    df['Movie'] = df['Movie'].astype('category').cat.codes + 1
    return df[['Nominee', 'Year', 'Category', 'Movie', 'Winner']]

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_9/training_4.csv"
]

dfs = [load_and_prepare_source(p) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby(['Nominee', 'Year', 'Category', 'Movie'], as_index=False).agg(
    Winner=('Winner', 'sum')
)

agg['Year'] = agg['Year'].astype(int)
agg['Category'] = agg['Category'].astype(int)
agg['Movie'] = agg['Movie'].astype(int)
agg['Winner'] = agg['Winner'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_9/target_multisource_mcts.csv", index=False)