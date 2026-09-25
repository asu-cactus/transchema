import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

for col in ['title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']:
    if col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
        df[col] = df[col].astype(str)
    if col in ['salary', 'rate', 'reviews']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

df['title'] = df['title'].astype('category').cat.codes + 1
df['location'] = df['location'].astype('category').cat.codes + 1
df['summary'] = df['summary'].astype('category').cat.codes + 1
df['href'] = df['href'].astype('category').cat.codes + 1
df['org_salary_period'] = df['org_salary_period'].astype('category').cat.codes + 1

df['company'] = df['company'].astype(str)

df['rate'] = df['rate'].fillna(0).astype(int)
df['reviews'] = df['reviews'].fillna(0).astype(int)
df['salary'] = df['salary'].fillna(0).astype(int)

df = df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)