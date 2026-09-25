import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Extract edition number from Year string, e.g. '2010 (83rd)' -> 83
df['Year'] = df['Year'].str.extract(r'\((\d+)[a-z]{2}\)')[0].astype(int)

df['Winner'] = df['Winner'].map({'YES': 1}).fillna(0).astype(int)

agg = df.groupby(['Category', 'Year']).agg(
    Nominee=('Nominee', 'count'),
    Movie=('Movie', 'count'),
    Winner=('Winner', 'sum')
).reset_index()

agg = agg[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)