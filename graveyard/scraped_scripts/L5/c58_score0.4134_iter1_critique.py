import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_58/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)

df['Winner'] = df['Winner'].map({'YES': 1}).fillna(0).astype(int)

# Group by Category and Year
agg_df = df.groupby(['Category', 'Year']).agg(
    Nominee=pd.NamedAgg(column='Nominee', aggfunc=lambda x: x.nunique()),
    Movie=pd.NamedAgg(column='Movie', aggfunc=lambda x: x.nunique()),
    Winner=pd.NamedAgg(column='Winner', aggfunc='sum')
).reset_index()

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_58/target_multisource_mcts.csv", index=False)