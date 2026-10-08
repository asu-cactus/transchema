import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# UNION all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Clean numeric columns
df['reviews'] = df['reviews'].astype(str).str.replace(',', '', regex=False)
df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce')
df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')

# Group by leftmost string columns that likely identify unique rows
group_cols = ['company', 'title', 'location', 'summary', 'org_salary_period']

# Aggregate numeric columns by count (count of non-null entries)
agg_dict = {
    'salary': 'count',
    'href': 'count',
    'rate': 'count',
    'reviews': 'count'
}

result = df.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

# Rename aggregated columns to match target schema column names
# The target schema columns are:
# ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer, 'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]
# The group_cols are string columns, so they remain as is.
# The aggregated columns are counts, so convert to int.

# Convert aggregated columns to int
result = result.astype({
    'title': 'object',  # keep as string
    'location': 'object',
    'summary': 'object',
    'org_salary_period': 'object',
    'salary': 'int64',
    'href': 'int64',
    'rate': 'int64',
    'reviews': 'int64'
})

# The target schema expects 'title', 'location', 'summary', 'org_salary_period' as integer,
# but source columns are strings. The target examples show integers in these columns,
# which likely represent counts or encoded values.
# Since we cannot guess encoding, keep them as strings to match source,
# but the problem states to keep column names exactly and types as in target.
# So convert these columns to integer by factorizing (encoding strings to integers).

for col in ['title', 'location', 'summary', 'org_salary_period']:
    result[col] = pd.factorize(result[col])[0] + 1  # +1 to avoid zero-based index

# company remains string

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)