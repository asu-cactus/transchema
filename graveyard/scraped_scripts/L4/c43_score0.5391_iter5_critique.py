import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean and convert columns to match target schema types
# Target schema: ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]

# 'company' is string, keep as is
df_all['company'] = df_all['company'].astype(str)

# Columns to convert to integer:
int_cols = ['title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']

# The source columns are not integer but string or float, so we need to convert them properly.
# For 'reviews', some values have commas, remove commas first
df_all['reviews'] = df_all['reviews'].astype(str).str.replace(',', '', regex=False)

# For 'org_salary_period', convert to categorical codes (integer)
df_all['org_salary_period'] = df_all['org_salary_period'].astype('category').cat.codes

# For 'title', 'location', 'summary', 'href' columns, these are strings in source but integers in target.
# We can convert them to categorical codes to get integer representation
for col in ['title', 'location', 'summary', 'href']:
    df_all[col] = df_all[col].astype(str).astype('category').cat.codes

# For 'salary', 'rate', 'reviews' convert to numeric integers
df_all['salary'] = pd.to_numeric(df_all['salary'], errors='coerce').fillna(0).astype(int)
df_all['rate'] = pd.to_numeric(df_all['rate'], errors='coerce').fillna(0).astype(int)
df_all['reviews'] = pd.to_numeric(df_all['reviews'], errors='coerce').fillna(0).astype(int)

# Remove duplicate rows to match target tuple count approximately
df_all = df_all.drop_duplicates()

# Write to target CSV with exact column order as target schema
target_columns = ['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
df_all[target_columns].to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)