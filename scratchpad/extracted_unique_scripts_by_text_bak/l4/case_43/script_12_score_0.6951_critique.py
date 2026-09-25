import pandas as pd
import numpy as np

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean and convert numeric columns
df_all['reviews'] = df_all['reviews'].astype(str).str.replace(',', '').astype(float)
df_all['rate'] = pd.to_numeric(df_all['rate'], errors='coerce')
df_all['salary'] = pd.to_numeric(df_all['salary'], errors='coerce')

# Encode categorical columns to integers starting from 1
df_all['title'] = df_all['title'].astype('category').cat.codes + 1
df_all['location'] = df_all['location'].astype('category').cat.codes + 1
df_all['summary'] = df_all['summary'].astype('category').cat.codes + 1
df_all['org_salary_period'] = df_all['org_salary_period'].astype('category').cat.codes + 1

# Group by company (string), and encoded integer columns
agg = df_all.groupby(['company', 'title', 'location', 'summary', 'org_salary_period'], dropna=False).agg(
    href=('href', 'count'),
    salary=('salary', 'mean'),
    rate=('rate', 'mean'),
    reviews=('reviews', 'mean')
).reset_index()

# Round aggregated floats to integers as per target schema
agg['salary'] = agg['salary'].round().astype('Int64')
agg['href'] = agg['href'].astype('Int64')
agg['rate'] = agg['rate'].round().astype('Int64')
agg['reviews'] = agg['reviews'].round().astype('Int64')

# Reorder columns to target schema order
agg = agg[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)