import pandas as pd
import numpy as np

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Extract SideA data
df_a = df[['WarNum', 'WarName', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()
df_a.columns = ['WarID', 'PolityName', 'PolityID', 'Side', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

# Extract SideB data
df_b = df[['WarNum', 'WarName', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()
df_b.columns = ['WarID', 'PolityName', 'PolityID', 'Side', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']

# Filter out rows with missing PolityID
df_a = df_a[df_a['PolityID'].notna()]
df_b = df_b[df_b['PolityID'].notna()]

# Concatenate SideA and SideB data (UNION)
df_all = pd.concat([df_a, df_b], ignore_index=True)

# Convert numeric columns to int, fill NaN with 0 for numeric columns only
for col in ['WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']:
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

# Group by key columns and sum Deaths
group_by_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']
df_grouped = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)