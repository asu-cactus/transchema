import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['title'] = pd.to_numeric(df['title'], errors='coerce').fillna(df['title'])
df['location'] = pd.to_numeric(df['location'], errors='coerce').fillna(df['location'])
df['summary'] = pd.to_numeric(df['summary'], errors='coerce').fillna(df['summary'])
df['salary'] = pd.to_numeric(df['salary'], errors='coerce').fillna(df['salary'])
df['href'] = pd.to_numeric(df['href'], errors='coerce').fillna(df['href'])
df['rate'] = pd.to_numeric(df['rate'], errors='coerce').fillna(df['rate'])
df['reviews'] = pd.to_numeric(df['reviews'].str.replace(',', ''), errors='coerce').fillna(df['reviews'])
df['org_salary_period'] = pd.to_numeric(df['org_salary_period'], errors='coerce').fillna(df['org_salary_period'])

df = df.rename(columns={
    'title': 'title',
    'company': 'company',
    'location': 'location',
    'summary': 'summary',
    'salary': 'salary',
    'href': 'href',
    'rate': 'rate',
    'reviews': 'reviews',
    'org_salary_period': 'org_salary_period'
})

df = df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)