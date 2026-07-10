import pandas as pd

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Ensure 'location' is string type for grouping
df['location'] = df['location'].astype(str)

# Group by 'location' and aggregate by counting non-null values in each column except 'location'
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

df_grouped = df.groupby('location', dropna=False).agg(agg_dict).reset_index()

# Rename columns to match target schema exactly (already matched)
df_target = df_grouped[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write to output CSV
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)