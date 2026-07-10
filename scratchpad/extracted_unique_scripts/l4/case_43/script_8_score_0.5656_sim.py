import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['title'] = pd.to_numeric(df['title'], errors='coerce').fillna(0).astype(int)
df['location'] = pd.to_numeric(df['location'], errors='coerce').fillna(0).astype(int)
df['summary'] = pd.to_numeric(df['summary'], errors='coerce').fillna(0).astype(int)
df['salary'] = pd.to_numeric(df['salary'], errors='coerce').fillna(0).astype(int)
df['href'] = pd.to_numeric(df['href'], errors='coerce').fillna(0).astype(int)
df['rate'] = pd.to_numeric(df['rate'], errors='coerce').fillna(0).astype(int)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0).astype(int)
df['org_salary_period'] = pd.to_numeric(df['org_salary_period'], errors='coerce').fillna(0).astype(int)

df = df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)