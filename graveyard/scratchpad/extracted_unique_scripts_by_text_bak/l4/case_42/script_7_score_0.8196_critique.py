import pandas as pd
import numpy as np

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean 'reviews' column: remove commas, convert to numeric, fill NaN with 0, convert to int
df['reviews'] = df['reviews'].astype(str).str.replace(',', '', regex=False)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0).astype(int)

# Convert 'rate' to numeric (float)
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')

# Define a helper function to get mode, fallback to first if mode empty
def mode_or_first(series):
    m = series.mode(dropna=True)
    if m.empty:
        # If all NaN, return NaN
        return np.nan
    else:
        return m.iloc[0]

# Group by 'location' only
agg = df.groupby('location', dropna=False).agg(
    title_mode = ('title', mode_or_first),
    company_mode = ('company', mode_or_first),
    summary_mode = ('summary', mode_or_first),
    salary_mean = ('salary', 'mean'),
    rate_mean = ('rate', 'mean'),
    reviews_sum = ('reviews', 'sum'),
    org_salary_period_mode = ('org_salary_period', mode_or_first)
).reset_index()

# Encode categorical columns to integer codes starting from 1
agg['title'] = agg['title_mode'].astype('category').cat.codes + 1
agg['company'] = agg['company_mode'].astype('category').cat.codes + 1
agg['summary'] = agg['summary_mode'].astype('category').cat.codes + 1
agg['org_salary_period'] = agg['org_salary_period_mode'].astype('category').cat.codes + 1

# Round numeric columns and convert to int
agg['salary'] = agg['salary_mean'].round().astype(int)
agg['rate'] = agg['rate_mean'].round().astype(int)
agg['reviews'] = agg['reviews_sum'].astype(int)

# Assign constant 1 to href as target expects integer
agg['href'] = 1

# Select and order columns as per target schema
agg = agg[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)