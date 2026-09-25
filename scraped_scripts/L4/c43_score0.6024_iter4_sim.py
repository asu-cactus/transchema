import pandas as pd
import numpy as np

# Load all source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# Concatenate all sources (schemas are the same)
df_all = pd.concat([src0, src1, src2, src3], ignore_index=True)

# Normalize 'rate' and 'reviews' columns: remove commas and convert to numeric
df_all['rate'] = pd.to_numeric(df_all['rate'].astype(str).str.replace(',', ''), errors='coerce')
df_all['reviews'] = pd.to_numeric(df_all['reviews'].astype(str).str.replace(',', ''), errors='coerce')

# Normalize 'title', 'location', 'summary', 'href', 'org_salary_period' columns to integer codes or numeric as needed
# For 'title', 'location', 'summary', 'href', 'org_salary_period' convert categorical/text columns to integer codes
for col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
    df_all[col] = df_all[col].astype(str).fillna('nan')
    df_all[col] = df_all[col].astype('category').cat.codes.replace(-1, np.nan)

# Group by company, title, location and aggregate averages for salary, rate, reviews
grouped = df_all.groupby(['company', 'title', 'location'], dropna=False).agg({
    'salary': 'mean',
    'rate': 'mean',
    'reviews': 'mean',
    'summary': 'first',
    'href': 'first',
    'org_salary_period': 'first'
}).reset_index()

# Convert aggregated columns to integer as target schema expects integer types
for col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
    grouped[col] = grouped[col].astype('Int64')

for col in ['salary', 'rate', 'reviews']:
    grouped[col] = grouped[col].round().astype('Int64')

# Reorder columns to match target schema
target_cols = ['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
result = grouped[target_cols]

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)