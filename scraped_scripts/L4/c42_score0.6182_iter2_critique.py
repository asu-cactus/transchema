import pandas as pd
import numpy as np

# Load all source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# UNION all sources
df = pd.concat([src0, src1, src2, src3], ignore_index=True)

# Clean and convert columns for aggregation
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['reviews'] = df['reviews'].astype(str).str.replace(',', '', regex=False)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce')

# Factorize categorical columns to get consistent integer IDs
# Factorize in the order: title, company, summary, org_salary_period
df['title'] = pd.factorize(df['title'])[0] + 1
df['company'] = pd.factorize(df['company'])[0] + 1
df['summary'] = pd.factorize(df['summary'])[0] + 1
df['org_salary_period'] = pd.factorize(df['org_salary_period'])[0] + 1

# Drop rows with NaN in group by columns to avoid grouping issues
df = df.dropna(subset=['location', 'title', 'company', 'summary', 'org_salary_period'])

# Group by location (string), and factorized integer columns
grouped = df.groupby(['location', 'title', 'company', 'summary', 'org_salary_period'], dropna=False).agg(
    href=('href', 'count'),
    salary=('salary', 'mean'),
    rate=('rate', 'mean'),
    reviews=('reviews', 'mean')
).reset_index()

# Convert aggregated columns to integer as target schema expects integer
grouped['salary'] = grouped['salary'].round().fillna(0).astype(int)
grouped['href'] = grouped['href'].fillna(0).astype(int)
grouped['rate'] = grouped['rate'].round().fillna(0).astype(int)
grouped['reviews'] = grouped['reviews'].round().fillna(0).astype(int)

# Reorder columns to match target schema
result = grouped[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)