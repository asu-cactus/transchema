import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

target_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

def fix_types(df):
    # Ensure all columns exist
    for col in target_cols:
        if col not in df.columns:
            # For missing PolityName in s2, fill with empty string
            if col == 'PolityName':
                df[col] = ''
            else:
                df[col] = pd.NA

    # Map Side from 'A'/'B' to 1/2, else NA
    df['Side'] = df['Side'].map({'A':1, 'B':2}).astype('Int64')

    # Convert numeric columns to Int64, coercing errors to NA
    int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    # PolityName as string
    df['PolityName'] = df['PolityName'].astype(str)

    # Reorder columns to target schema
    df = df[target_cols]

    return df

s0 = fix_types(s0)
s1 = fix_types(s1)
s2 = fix_types(s2)
s3 = fix_types(s3)

# Concatenate all sources
result = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)