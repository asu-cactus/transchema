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

df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce')

agg = df.groupby('Initiator').agg(
    WarID_count=('WarID', 'count'),
    Deaths_sum=('Deaths', 'sum'),
    Outcome_avg=('Outcome', 'mean')
).reset_index()

# The partial plan only aggregates by Initiator, but target schema requires all columns:
# The target schema is ['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']
# The partial plan aggregates only on Initiator, which loses other columns.
# So the partial plan is insufficient to produce the target schema.
# We must produce the target table by unioning all sources (all have same schema), then convert columns to correct types.
# The partial plan's aggregation is not consistent with the target schema (which has all columns, not aggregated).
# Therefore, the correct plan is to UNION all sources, then convert columns to correct types, no aggregation.

# So we override the plan to:
# UNION all sources
# NO_MORE_OPERATION

# Implementing the corrected plan:

df_all = df.copy()

# Convert columns to target types:
# Target schema types:
# 'Outcome': integer
# 'WarID': integer
# 'PolityName': integer
# 'StartYear': integer
# 'StartMonth': integer
# 'StartDay': integer
# 'EndYear': integer
# 'EndMonth': integer
# 'EndDay': integer
# 'Initiator': integer
# 'Deaths': integer

# PolityName and Initiator are strings in source, but target expects integer.
# From examples, Initiator looks like categorical integer codes (e.g., 127, 21, 10)
# But source Initiator is string like 'A', 'B', or '127'?
# Source examples show Initiator as strings like 'A', 'B', or '127' (mixed).
# We must convert Initiator and PolityName to integer codes.

# PolityName is string in source, target expects integer.
# We will encode PolityName and Initiator as categorical codes (starting from 1).

df_all['PolityName'] = df_all['PolityName'].astype(str)
df_all['Initiator'] = df_all['Initiator'].astype(str)

df_all['PolityName'] = pd.Categorical(df_all['PolityName']).codes + 1
df_all['Initiator'] = pd.Categorical(df_all['Initiator']).codes + 1

# Convert numeric columns to integers, filling NaN with 0
for col in ['Outcome', 'WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Deaths']:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

# Select columns in target order
df_all = df_all[['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)