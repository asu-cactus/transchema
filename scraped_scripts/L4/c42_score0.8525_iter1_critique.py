import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean 'reviews' column by removing commas
df['reviews'] = df['reviews'].astype(str).str.replace(',', '', regex=False)

# Group by 'location' and aggregate by count distinct for other columns
agg_dict = {
    'title': pd.Series.nunique,
    'company': pd.Series.nunique,
    'summary': pd.Series.nunique,
    'salary': pd.Series.nunique,
    'href': pd.Series.nunique,
    'rate': pd.Series.nunique,
    'reviews': pd.Series.nunique,
    'org_salary_period': pd.Series.nunique
}

result = df.groupby('location', dropna=False).agg(agg_dict).reset_index()

# Ensure columns order matches target schema
result = result[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Convert all columns except 'location' to int (counts)
for col in result.columns[1:]:
    result[col] = result[col].fillna(0).astype(int)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)