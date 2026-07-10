import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_42/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_42/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_42/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_42/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Ensure 'location' is string
df['location'] = df['location'].astype(str)

# Columns as per source schema
cat_cols = ['title', 'company', 'summary', 'href', 'org_salary_period']
num_cols = ['salary', 'rate', 'reviews']

# Convert categorical columns to category dtype and then to codes
for col in cat_cols:
    df[col] = df[col].astype('category').cat.codes

# Convert numeric columns to numeric, coerce errors to NaN
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Define aggregation functions
def mode_agg(series):
    # Return the mode if exists, else first value
    modes = series.mode()
    if not modes.empty:
        return modes.iloc[0]
    else:
        return series.iloc[0]

agg_dict = {
    'title': mode_agg,
    'company': mode_agg,
    'summary': mode_agg,
    'salary': 'mean',
    'href': mode_agg,
    'rate': 'mean',
    'reviews': 'sum',
    'org_salary_period': mode_agg
}

grouped = df.groupby('location').agg(agg_dict)

# Round numeric columns to int as target schema expects int
grouped['salary'] = grouped['salary'].round().astype(int)
grouped['rate'] = grouped['rate'].round().astype(int)
grouped['reviews'] = grouped['reviews'].fillna(0).astype(int)

# Ensure all other columns are int
for col in ['title', 'company', 'summary', 'href', 'org_salary_period']:
    grouped[col] = grouped[col].astype(int)

# Reset index to have 'location' as a column
result = grouped.reset_index()

# Reorder columns as per target schema
result = result[['location', 'title', 'company', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts.csv", index=False)