import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['reviews'] = df['reviews'].astype(str).str.replace(',', '').astype(float)
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')

agg_dict = {
    'title': 'count',
    'location': 'count',
    'summary': 'count',
    'salary': 'count',
    'href': 'count',
    'rate': 'count',
    'reviews': 'count',
    'org_salary_period': 'count'
}

result = df.groupby('company', dropna=False).agg(agg_dict).reset_index()

result = result.astype({
    'title': 'int64',
    'location': 'int64',
    'summary': 'int64',
    'salary': 'int64',
    'href': 'int64',
    'rate': 'int64',
    'reviews': 'int64',
    'org_salary_period': 'int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)