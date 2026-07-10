import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['location'] = df['location'].astype(str)

df['title'] = pd.to_numeric(df['title'], errors='coerce').fillna(df['title'])
df['company'] = pd.to_numeric(df['company'], errors='coerce').fillna(df['company'])
df['summary'] = pd.to_numeric(df['summary'], errors='coerce').fillna(df['summary'])
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
df['href'] = pd.to_numeric(df['href'], errors='coerce').fillna(df['href'])
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['reviews'] = pd.to_numeric(df['reviews'].str.replace(',', ''), errors='coerce')
df['org_salary_period'] = pd.to_numeric(df['org_salary_period'], errors='coerce').fillna(df['org_salary_period'])

df = df[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)