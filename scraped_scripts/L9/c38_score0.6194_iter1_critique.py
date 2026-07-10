import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_38/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all source tables (UNION)
df = pd.concat(dfs, ignore_index=True)

# Select only relevant columns
df = df[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to integer (coerce errors to NaN, then drop)
df['funded_year'] = pd.to_numeric(df['funded_year'], errors='coerce').dropna().astype(int)

# Convert raised_amount_usd to numeric, coerce errors to NaN (will be ignored in sum)
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce')

# Drop rows with NaN in company_permalink or funded_year (key columns)
df = df.dropna(subset=['company_permalink', 'funded_year'])

# Group by company_permalink and funded_year, sum raised_amount_usd
result = df.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

# Convert raised_amount_usd to integer (as in target schema)
result['raised_amount_usd'] = result['raised_amount_usd'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_38/target_multisource_mcts.csv", index=False)