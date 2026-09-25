import pandas as pd
from scipy.stats import mode

def load_and_prepare(path):
    df = pd.read_csv(path, index_col=0)
    # Normalize 'reviews' column: remove commas and convert to float
    df['reviews'] = df['reviews'].astype(str).str.replace(',', '').astype(float)
    # Normalize 'org_salary_period' to lowercase stripped strings for consistent encoding
    df['org_salary_period'] = df['org_salary_period'].astype(str).str.lower().str.strip()
    # Convert 'title' and 'location' to categorical codes +1 to match target integer encoding
    df['title'] = df['title'].astype('category').cat.codes + 1
    df['location'] = df['location'].astype('category').cat.codes + 1
    # 'company' remains string
    # 'href' presence count per row
    df['href'] = 1
    return df

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv"
]

dfs = [load_and_prepare(p) for p in paths]

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Encode 'org_salary_period' as categorical codes for aggregation
df_all['org_salary_period'] = df_all['org_salary_period'].astype('category').cat.codes + 1

# Define aggregation functions
def mode_agg(series):
    # mode returns ModeResult, take first mode value
    m = mode(series, nan_policy='omit')
    if m.count[0] == 0:
        return pd.NA
    return m.mode[0]

# Aggregate summary by average length of string
def avg_len(series):
    lengths = series.astype(str).str.len()
    return round(lengths.mean())

# Group by 'company' only
agg_df = df_all.groupby('company', dropna=False).agg(
    title = lambda x: mode_agg(x),
    location = lambda x: mode_agg(x),
    summary = lambda x: avg_len(x),
    salary = lambda x: round(x.mean()),
    href = 'count',
    rate = lambda x: round(x.mean()),
    reviews = lambda x: round(x.sum()),
    org_salary_period = lambda x: mode_agg(x)
).reset_index()

# Convert all columns to int where appropriate
agg_df['title'] = agg_df['title'].astype('Int64')
agg_df['location'] = agg_df['location'].astype('Int64')
agg_df['summary'] = agg_df['summary'].astype('Int64')
agg_df['salary'] = agg_df['salary'].astype('Int64')
agg_df['href'] = agg_df['href'].astype('Int64')
agg_df['rate'] = agg_df['rate'].astype('Int64')
agg_df['reviews'] = agg_df['reviews'].astype('Int64')
agg_df['org_salary_period'] = agg_df['org_salary_period'].astype('Int64')

# Reorder columns to match target schema
agg_df = agg_df[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)