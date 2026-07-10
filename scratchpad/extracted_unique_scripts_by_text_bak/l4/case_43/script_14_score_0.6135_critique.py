import pandas as pd
from scipy.stats import mode

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean numeric columns: remove commas, convert to numeric
for col in ['salary', 'rate', 'reviews']:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# Fill NaNs in numeric columns with 0 before aggregation
df['salary'] = df['salary'].fillna(0)
df['rate'] = df['rate'].fillna(0)
df['reviews'] = df['reviews'].fillna(0)

# Convert categorical columns to string for consistent mode calculation
for col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
    df[col] = df[col].astype(str)

# Define aggregation functions
def mode_agg(series):
    # mode returns ModeResult, take first mode if exists, else NaN
    m = mode(series, nan_policy='omit')
    if m.count[0] > 0:
        return m.mode[0]
    else:
        return pd.NA

agg_dict = {
    'title': mode_agg,
    'location': mode_agg,
    'summary': mode_agg,
    'salary': 'mean',
    'href': mode_agg,
    'rate': 'mean',
    'reviews': 'mean',
    'org_salary_period': mode_agg
}

# Group by 'company' and aggregate
grouped = df.groupby('company').agg(agg_dict).reset_index()

# Convert categorical aggregated columns to category codes +1 (to match target)
for col in ['title', 'location', 'summary', 'href', 'org_salary_period']:
    grouped[col] = grouped[col].astype('category').cat.codes + 1

# Convert numeric columns to int
for col in ['salary', 'rate', 'reviews']:
    grouped[col] = grouped[col].round().astype(int)

# Reorder columns to match target schema
grouped = grouped[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)