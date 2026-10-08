import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# UNION all source tables (concatenate rows)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY 'location' and count all other columns
agg = df_all.groupby("location").agg(
    title=('title', 'count'),
    company=('company', 'count'),
    summary=('summary', 'count'),
    salary=('salary', 'count'),
    href=('href', 'count'),
    rate=('rate', 'count'),
    reviews=('reviews', 'count'),
    org_salary_period=('org_salary_period', 'count')
).reset_index()

# Write output with exact target schema column names
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)