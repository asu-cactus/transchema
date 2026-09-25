import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['location'] = df['location'].astype(str)

int_cols = ['title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']

for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df = df[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)