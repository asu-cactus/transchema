import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Ensure 'location' is string type
df['location'] = df['location'].astype(str)

# Columns to encode as integers (categorical columns except 'location')
categorical_cols = ['title', 'company', 'summary', 'href', 'org_salary_period']

for col in categorical_cols:
    # Factorize to get integer codes, NaNs become -1, replace with NaN
    codes, uniques = pd.factorize(df[col])
    codes = pd.Series(codes)
    codes = codes.replace(-1, pd.NA)
    df[col] = codes.astype('Int64')

# Convert numeric columns to integers
# 'salary', 'rate', 'reviews' may have NaNs, convert carefully
df['salary'] = pd.to_numeric(df['salary'], errors='coerce').round().astype('Int64')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce').round().astype('Int64')

# Remove commas from 'reviews' and convert to int
df['reviews'] = df['reviews'].astype(str).str.replace(',', '', regex=False)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').round().astype('Int64')

# Reorder columns to match target schema exactly
df = df[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write to output CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)