import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['title'] = df_all['title'].astype(str)
df_all['company'] = df_all['company'].astype(str)
df_all['location'] = df_all['location'].astype(str)
df_all['summary'] = df_all['summary'].astype(str)
df_all['href'] = df_all['href'].astype(str)
df_all['org_salary_period'] = df_all['org_salary_period'].astype(str)

def to_int_safe(x):
    try:
        return int(float(str(x).replace(',','')))
    except:
        return 0

df_all['salary'] = df_all['salary'].apply(to_int_safe)
df_all['rate'] = df_all['rate'].apply(to_int_safe)
df_all['reviews'] = df_all['reviews'].apply(to_int_safe)

grouped = df_all.groupby('location', dropna=False).agg({
    'title': 'count',
    'company': 'count',
    'summary': 'count',
    'salary': 'count',
    'href': 'count',
    'rate': 'count',
    'reviews': 'count',
    'org_salary_period': 'count'
}).reset_index()

grouped = grouped.rename(columns={
    'title': 'title',
    'company': 'company',
    'summary': 'summary',
    'salary': 'salary',
    'href': 'href',
    'rate': 'rate',
    'reviews': 'reviews',
    'org_salary_period': 'org_salary_period'
})

grouped = grouped.astype({
    'title': int,
    'company': int,
    'summary': int,
    'salary': int,
    'href': int,
    'rate': int,
    'reviews': int,
    'org_salary_period': int
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)