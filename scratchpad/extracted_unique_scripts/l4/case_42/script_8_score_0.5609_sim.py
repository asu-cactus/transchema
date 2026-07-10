import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['reviews'] = df['reviews'].astype(str).str.replace(',', '').replace('nan', '0')
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0).astype(int)

df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

agg = df.groupby(['location', 'title', 'company', 'summary', 'org_salary_period'], dropna=False).agg(
    salary_count = ('salary', 'count'),
    salary_avg = ('salary', 'mean'),
    rate_avg = ('rate', 'mean'),
    reviews_sum = ('reviews', 'sum')
).reset_index()

agg['title'] = agg['title'].astype('category').cat.codes + 1
agg['company'] = agg['company'].astype('category').cat.codes + 1
agg['summary'] = agg['summary'].astype('category').cat.codes + 1
agg['org_salary_period'] = agg['org_salary_period'].astype('category').cat.codes + 1

agg['salary'] = agg['salary_avg'].round().astype(int)
agg['rate'] = agg['rate_avg'].round().astype(int)
agg['reviews'] = agg['reviews_sum'].astype(int)

agg = agg.rename(columns={'location':'location'})

agg = agg[['location', 'title', 'company', 'summary', 'salary', 'rate', 'reviews', 'org_salary_period']]

agg['href'] = 1

agg = agg[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)