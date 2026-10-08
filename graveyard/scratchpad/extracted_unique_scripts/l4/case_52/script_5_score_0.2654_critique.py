import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

# Source3 lacks PolityName column, add it with NaN
if 'PolityName' not in src3.columns:
    src3['PolityName'] = pd.NA

# Concatenate all sources
df = pd.concat([src0, src1, src2, src3], ignore_index=True, sort=False)

# Convert columns to appropriate types
# Use Int64 dtype to allow NaN integers
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Outcome']

for col in int_cols:
    df[col] = df[col].astype('Int64')

# Side conversion: map 'A'->1, 'B'->0, numeric strings to int, else NA
def side_to_int(x):
    if pd.isna(x):
        return pd.NA
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        return int(x)
    if isinstance(x, str):
        if x.isdigit():
            return int(x)
        if x.upper() == 'A':
            return 1
        if x.upper() == 'B':
            return 0
    return pd.NA

df['Side'] = df['Side'].apply(side_to_int).astype('Int64')

# Deaths: convert to Int64 (sum aggregation later)
df['Deaths'] = df['Deaths'].astype('Int64')

# PolityName: convert to int if possible, else NA
def polityname_to_int(x):
    try:
        return int(x)
    except:
        return pd.NA

df['PolityName'] = df['PolityName'].apply(polityname_to_int).astype('Int64')

# Define group by columns (leftmost key columns in target schema)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome']

# Aggregate Deaths by sum, PolityName by max (to get a representative integer)
agg_dict = {
    'Deaths': 'sum',
    'PolityName': 'max'
}

df_agg = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_agg = df_agg[target_cols]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)