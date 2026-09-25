import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

join_cols = ['title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
df_joined = pd.merge(df0, df1, on=join_cols, how='outer')

df_all = pd.concat([df_joined, df2, df3], ignore_index=True)

agg_df = df_all.groupby('company').agg(
    title=('title', 'count'),
    location=('location', 'count'),
    summary=('summary', 'count'),
    salary=('salary', 'count'),
    href=('href', 'count'),
    rate=('rate', 'count'),
    reviews=('reviews', 'count'),
    org_salary_period=('org_salary_period', 'count')
).reset_index()

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)