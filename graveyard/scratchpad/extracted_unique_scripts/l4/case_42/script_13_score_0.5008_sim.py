import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

join_0 = pd.merge(df0, df1, on="location", suffixes=('_0', '_1'))
join_1 = pd.merge(join_0, df2, on="location", suffixes=('', '_2'))
join_2 = pd.merge(join_1, df3, on="location", suffixes=('', '_3'))

agg = join_2.groupby("location").agg(
    title=('title_0', 'count'),
    company=('company_0', 'count'),
    summary=('summary_0', 'count'),
    salary=('salary_0', 'count'),
    href=('href_0', 'count'),
    rate=('rate_0', 'count'),
    reviews=('reviews_0', 'count'),
    org_salary_period=('org_salary_period_0', 'count')
).reset_index()

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)