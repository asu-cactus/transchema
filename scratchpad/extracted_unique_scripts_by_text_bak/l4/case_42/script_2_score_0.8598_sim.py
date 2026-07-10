import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['reviews'] = df['reviews'].astype(str).str.replace(',', '').replace('nan', pd.NA)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce')

agg_dict = {
    'title': 'count',
    'company': 'count',
    'summary': 'count',
    'salary': 'count',
    'href': 'count',
    'rate': 'count',
    'reviews': 'count',
    'org_salary_period': 'count'
}

result = df.groupby('location', dropna=False).agg(agg_dict).reset_index()

result = result.astype({
    'title': 'Int64',
    'company': 'Int64',
    'summary': 'Int64',
    'salary': 'Int64',
    'href': 'Int64',
    'rate': 'Int64',
    'reviews': 'Int64',
    'org_salary_period': 'Int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)