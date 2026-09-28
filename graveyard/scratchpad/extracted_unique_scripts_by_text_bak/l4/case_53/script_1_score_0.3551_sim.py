import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

s1_2 = pd.merge(
    s1,
    s2,
    how="inner",
    left_on=["WarID", "PolityID", "StartYear"],
    right_on=["WarID", "PolityID", "StartYear"],
    suffixes=("", "_s2"),
)

# After join, drop duplicate columns from s2 (those that exist in s1)
cols_to_drop = [c for c in s1_2.columns if c.endswith("_s2")]
s1_2 = s1_2.drop(columns=cols_to_drop)

# Ensure all columns match target schema and types
# Target columns: ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
# s2 has no PolityName, so keep s1's PolityName

# Reorder columns to target schema order
target_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

def fix_types(df):
    for col in ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']:
        if col in df.columns:
            if col == 'Side':
                # Side is integer in target but source has strings like 'A', 'B'
                # Map 'A'->1, 'B'->2, else NaN
                df[col] = df[col].map({'A':1, 'B':2}).astype('Int64')
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    if 'PolityName' in df.columns:
        df['PolityName'] = df['PolityName'].astype(str)
    return df

s0 = fix_types(s0)
s1_2 = fix_types(s1_2)
s3 = fix_types(s3)

# Select only target columns (some sources may have extra columns)
s0 = s0[target_cols]
s1_2 = s1_2[target_cols]
s3 = s3[target_cols]

result = pd.concat([s0, s1_2, s3], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)