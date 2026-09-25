import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean numeric columns
df_all['reviews'] = pd.to_numeric(df_all['reviews'].astype(str).str.replace(',', ''), errors='coerce')
df_all['salary'] = pd.to_numeric(df_all['salary'], errors='coerce')
df_all['rate'] = pd.to_numeric(df_all['rate'], errors='coerce')

# Encode categorical columns as integer codes per company
# Columns to encode: title, location, summary, href, org_salary_period
# We encode these columns by taking the first non-null value per company, then factorize to integer codes

# Extract first non-null value per company for each categorical column
cat_cols = ['title', 'location', 'summary', 'href', 'org_salary_period']
first_values = df_all.groupby('company')[cat_cols].first().reset_index()

# Factorize each categorical column to integer codes
for col in cat_cols:
    # Factorize returns (codes, uniques)
    codes, uniques = pd.factorize(first_values[col])
    first_values[col] = codes + 1  # start codes from 1 to match target examples (avoid 0)

# Aggregate numeric columns by company
agg_numeric = df_all.groupby('company').agg(
    salary_avg=('salary', 'mean'),
    rate_avg=('rate', 'mean'),
    reviews_sum=('reviews', 'sum')
).reset_index()

# Round and convert to int
agg_numeric['salary'] = agg_numeric['salary_avg'].round().fillna(0).astype(int)
agg_numeric['rate'] = agg_numeric['rate_avg'].round().fillna(0).astype(int)
agg_numeric['reviews'] = agg_numeric['reviews_sum'].fillna(0).astype(int)

# Drop intermediate columns
agg_numeric = agg_numeric.drop(columns=['salary_avg', 'rate_avg', 'reviews_sum'])

# Merge encoded categorical columns with aggregated numeric columns on company
result = pd.merge(first_values, agg_numeric, on='company', how='inner')

# Reorder columns to match target schema:
# ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]

result = result[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)