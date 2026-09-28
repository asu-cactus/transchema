import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['location'] = df['location'].astype(str)

df['title'] = 1
df['company'] = 1
df['summary'] = 1
df['salary'] = 1
df['href'] = 1
df['rate'] = 1
df['reviews'] = 1
df['org_salary_period'] = 1

df_target = df[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)