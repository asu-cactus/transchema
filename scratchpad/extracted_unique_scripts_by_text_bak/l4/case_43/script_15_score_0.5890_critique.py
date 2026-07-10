import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Columns to encode as categorical codes (string columns that become integer codes)
cat_cols = ['title', 'location', 'summary', 'href', 'org_salary_period']

# Convert categorical columns to string and then to categorical codes
for col in cat_cols:
    df[col] = df[col].astype(str).str.strip()  # strip whitespace
    df[col] = pd.Categorical(df[col]).codes

# company remains string
df['company'] = df['company'].astype(str).str.strip()

# Convert numeric columns to numeric (salary, rate, reviews)
# Remove commas and convert to numeric
df['salary'] = pd.to_numeric(df['salary'].astype(str).str.replace(',', '').str.strip(), errors='coerce')
df['rate'] = pd.to_numeric(df['rate'].astype(str).str.replace(',', '').str.strip(), errors='coerce')
df['reviews'] = pd.to_numeric(df['reviews'].astype(str).str.replace(',', '').str.strip(), errors='coerce')

# Group by company and categorical columns, aggregate numeric columns by mean
group_cols = ['company', 'title', 'location', 'summary', 'href', 'org_salary_period']
agg_cols = ['salary', 'rate', 'reviews']

df_grouped = df.groupby(group_cols, dropna=False)[agg_cols].mean().reset_index()

# Convert aggregated numeric columns to int (rounding)
df_grouped['salary'] = df_grouped['salary'].round().astype('Int64')
df_grouped['rate'] = df_grouped['rate'].round().astype('Int64')
df_grouped['reviews'] = df_grouped['reviews'].round().astype('Int64')

# The target schema order:
# ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]

# Reorder columns to match target schema
df_final = df_grouped[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)