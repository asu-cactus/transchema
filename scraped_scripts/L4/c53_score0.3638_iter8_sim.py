import pandas as pd
import numpy as np

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

# Normalize Side columns to integer (A=1, B=2) if needed
def side_to_int(df):
    if df['Side'].dtype == object:
        df['Side'] = df['Side'].map({'A':1, 'B':2}).fillna(df['Side'])
    df['Side'] = pd.to_numeric(df['Side'], errors='coerce').fillna(0).astype(int)
    return df

s0 = side_to_int(s0)
s1 = side_to_int(s1)
s2 = side_to_int(s2)
s3 = side_to_int(s3)

# For s2, add missing PolityName column with NaN to align schema
if 'PolityName' not in s2.columns:
    s2['PolityName'] = np.nan

# Align columns order and types for union
cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

def prepare_df(df):
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    df = df[cols]
    # Convert numeric columns to appropriate types
    for c in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    # PolityName to string, fill NaN with empty string to avoid issues
    df['PolityName'] = df['PolityName'].astype(str).replace('nan', '')
    # Fill NaN numeric with 0 for integer columns where appropriate
    for c in ['PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']:
        df[c] = df[c].fillna(0).astype(int)
    # WarID keep as int, fillna 0
    df['WarID'] = df['WarID'].fillna(0).astype(int)
    return df

s0p = prepare_df(s0)
s1p = prepare_df(s1)
s3p = prepare_df(s3)
# s2 has no PolityName, so after adding NaN, prepare_df will fill with empty string
s2p = prepare_df(s2)

# Union s0, s1, s3 first (same schema)
union_0 = pd.concat([s0p, s1p, s3p], ignore_index=True)

# Then union with s2p
final_df = pd.concat([union_0, s2p], ignore_index=True)

# Reorder columns to target schema exactly
final_df = final_df[cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)