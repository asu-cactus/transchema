import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean 'reviews' column: remove commas, convert to numeric
df['reviews'] = df['reviews'].astype(str).str.replace(',', '', regex=False).replace('nan', pd.NA)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce')

# Define group by columns
group_by_cols = ['location', 'title']

# Define aggregation columns (all except group by)
agg_cols = ['company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']

# Aggregate: count of non-null values per group
agg_dict = {col: 'count' for col in agg_cols}

result = df.groupby(group_by_cols, dropna=False).agg(agg_dict).reset_index()

# Convert aggregated columns to Int64 dtype (nullable integer)
result = result.astype({col: 'Int64' for col in agg_cols})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)