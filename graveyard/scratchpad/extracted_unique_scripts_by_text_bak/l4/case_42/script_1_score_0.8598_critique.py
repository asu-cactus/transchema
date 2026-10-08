import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# Normalize 'location' by stripping whitespace
for df in [df0, df1, df2, df3]:
    df['location'] = df['location'].astype(str).str.strip()

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY 'location' and count non-null values for other columns
agg_df = df_all.groupby('location').agg({
    'title': 'count',
    'company': 'count',
    'summary': 'count',
    'salary': 'count',
    'href': 'count',
    'rate': 'count',
    'reviews': 'count',
    'org_salary_period': 'count'
}).reset_index()

# Rename columns to match target schema exactly
agg_df.columns = ['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)