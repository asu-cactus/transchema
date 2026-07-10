import pandas as pd

def clean_int_column(series):
    return pd.to_numeric(series.astype(str).str.replace(',', '').str.extract(r'(\d+)')[0], errors='coerce').fillna(0).astype(int)

def clean_float_column(series):
    return pd.to_numeric(series.astype(str).str.replace(',', ''), errors='coerce')

def count_distinct(series):
    return series.nunique()

def first_non_null(series):
    # Return first non-null value or NaN
    return series.dropna().iloc[0] if not series.dropna().empty else pd.NA

# Read all source CSVs
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean numeric columns
df['salary'] = clean_int_column(df['salary'])
df['rate'] = clean_float_column(df['rate'])
df['reviews'] = clean_int_column(df['reviews'])

# Ensure string columns are string type
df['href'] = df['href'].astype(str)
df['org_salary_period'] = df['org_salary_period'].astype(str)
df['location'] = df['location'].astype(str)
df['title'] = df['title'].astype(str)
df['company'] = df['company'].astype(str)

# Group by location only
grouped = df.groupby('location', dropna=False).agg(
    title=('title', first_non_null),
    company=('company', first_non_null),
    salary=('salary', 'min'),
    href=('href', pd.Series.nunique),
    rate=('rate', 'mean'),
    reviews=('reviews', 'min'),
    org_salary_period=('org_salary_period', pd.Series.nunique)
).reset_index()

# Set summary to constant 1 as target examples show
grouped['summary'] = 1

# Factorize title and company to integers starting from 1
grouped['title'] = pd.factorize(grouped['title'])[0] + 1
grouped['company'] = pd.factorize(grouped['company'])[0] + 1

# Convert rate to int by rounding (target schema expects int)
grouped['rate'] = grouped['rate'].round().astype(int)

# Ensure all columns have correct types
grouped['location'] = grouped['location'].astype(str)
grouped['summary'] = grouped['summary'].astype(int)
grouped['salary'] = grouped['salary'].astype(int)
grouped['href'] = grouped['href'].astype(int)
grouped['reviews'] = grouped['reviews'].astype(int)
grouped['org_salary_period'] = grouped['org_salary_period'].astype(int)

# Reorder columns to match target schema
result = grouped[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)