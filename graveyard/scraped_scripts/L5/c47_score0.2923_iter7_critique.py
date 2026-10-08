import pandas as pd
import numpy as np

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Convert columns to appropriate types
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce')

# Define aggregation functions
agg_dict = {
    'PolityName': 'first',
    'StartYear': 'first',
    'StartMonth': 'first',
    'StartDay': 'first',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Initiator': 'first',
    'Deaths': 'sum'
}

# Group by Outcome and WarID
agg = df.groupby(['Outcome', 'WarID'], dropna=False).agg(agg_dict).reset_index()

# Convert columns to integer types where appropriate
# PolityName and Initiator are strings, so keep as is
# For integer columns, fill NaN with 0 or keep as nullable Int64
agg['StartYear'] = agg['StartYear'].round().astype('Int64')
agg['StartMonth'] = agg['StartMonth'].round().astype('Int64')
agg['StartDay'] = agg['StartDay'].round().astype('Int64')
agg['EndYear'] = agg['EndYear'].round().astype('Int64')
agg['EndMonth'] = agg['EndMonth'].round().astype('Int64')
agg['EndDay'] = agg['EndDay'].round().astype('Int64')
agg['Deaths'] = agg['Deaths'].fillna(0).astype('Int64')

# Reorder columns to match target schema
agg = agg[['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
           'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)