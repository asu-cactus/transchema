import pandas as pd

def load_and_prepare(path):
    df = pd.read_csv(path, index_col=0)
    # Normalize 'reviews' column: remove commas and convert to float
    df['reviews'] = df['reviews'].astype(str).str.replace(',', '').astype(float)
    # Normalize 'org_salary_period' to lowercase stripped strings for consistent counting
    df['org_salary_period'] = df['org_salary_period'].astype(str).str.lower().str.strip()
    # Normalize 'title' and 'location' to categorical codes (integers)
    df['title'] = df['title'].astype('category').cat.codes + 1
    df['location'] = df['location'].astype('category').cat.codes + 1
    # 'company' remains string
    # Convert 'href' to countable presence (1 per row)
    df['href_count'] = 1
    return df

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv"
]

dfs = [load_and_prepare(p) for p in paths]

# Concatenate all source data
df_all = pd.concat(dfs, ignore_index=True)

# Group by company, title, location
grouped = df_all.groupby(['company', 'title', 'location'], dropna=False).agg(
    href=('href_count', 'count'),
    reviews=('reviews', 'sum'),
    org_salary_period_count=('org_salary_period', lambda x: x.nunique())
).reset_index()

# For other columns in target schema: summary, salary, rate
# We take mean of these columns grouped by company, title, location to get integer values
# Convert to int by rounding

agg_others = df_all.groupby(['company', 'title', 'location'], dropna=False).agg(
    summary=('summary', lambda x: round(x.astype(str).str.len().mean())),  # summary is string, convert to avg length as int
    salary=('salary', 'mean'),
    rate=('rate', 'mean')
).reset_index()

# Merge aggregated others with grouped counts
result = pd.merge(grouped, agg_others, on=['company', 'title', 'location'], how='left')

# Convert columns to int as per target schema
result['summary'] = result['summary'].fillna(0).astype(int)
result['salary'] = result['salary'].fillna(0).round().astype(int)
result['rate'] = result['rate'].fillna(0).round().astype(int)
result['href'] = result['href'].astype(int)
result['reviews'] = result['reviews'].round().astype(int)
result['org_salary_period'] = result['org_salary_period_count'].astype(int)

# Drop helper column
result = result.drop(columns=['org_salary_period_count'])

# Reorder columns to match target schema
result = result[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)