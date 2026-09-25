import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_44/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_44/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_44/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

for col in ['title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']:
    if col in ['title', 'company', 'location', 'summary', 'href']:
        df[col] = df[col].notna().astype(int)
    else:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)

result = df.groupby('org_salary_period', as_index=False).sum()

result = result[['org_salary_period', 'title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_44/target_multisource_mcts.csv", index=False)