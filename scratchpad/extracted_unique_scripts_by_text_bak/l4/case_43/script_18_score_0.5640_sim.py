import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['reviews'] = pd.to_numeric(df_all['reviews'].astype(str).str.replace(',', ''), errors='coerce')
df_all['salary'] = pd.to_numeric(df_all['salary'], errors='coerce')
df_all['rate'] = pd.to_numeric(df_all['rate'], errors='coerce')

group_cols = ['company', 'title', 'location', 'summary', 'href', 'org_salary_period']
agg_df = df_all.groupby(group_cols).agg(
    salary=('salary', 'count'),
    salary_avg=('salary', 'mean'),
    rate=('rate', 'mean'),
    reviews=('reviews', 'sum')
).reset_index()

agg_df['salary'] = agg_df['salary_avg'].round().fillna(0).astype(int)
agg_df['rate'] = agg_df['rate'].round().fillna(0).astype(int)
agg_df['reviews'] = agg_df['reviews'].fillna(0).astype(int)

agg_df = agg_df.drop(columns=['salary_avg'])

agg_df = agg_df.rename(columns={
    'salary': 'salary',
    'rate': 'rate',
    'reviews': 'reviews',
    'company': 'company',
    'title': 'title',
    'location': 'location',
    'summary': 'summary',
    'href': 'href',
    'org_salary_period': 'org_salary_period'
})

agg_df['title'] = 1
agg_df['location'] = 1
agg_df['summary'] = 1
agg_df['href'] = 1
agg_df['org_salary_period'] = 1

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)