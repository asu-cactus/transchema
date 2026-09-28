import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Source1 lacks PolityName, add it as NaN
df1['PolityName'] = pd.NA

# Define consistent column order
cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
        'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# Reorder columns for all dataframes
df0 = df0[cols]
df1 = df1[cols]
df2 = df2[cols]
df3 = df3[cols]

# Union all sources
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by primary key columns: Side, WarID, PolityID
group_cols = ['Side', 'WarID', 'PolityID']

# Define aggregation dictionary
agg_dict = {
    'StartYear': 'max',
    'StartMonth': 'max',
    'StartDay': 'max',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'IsInitiator': 'max',
    'Outcome': 'max',
    'Deaths': 'sum',
    'PolityName': lambda x: x.dropna().iloc[0] if not x.dropna().empty else pd.NA
}

agg_df = df_all.groupby(group_cols).agg(agg_dict).reset_index()

# Convert columns to integer where appropriate
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

for c in int_cols:
    agg_df[c] = pd.to_numeric(agg_df[c], errors='coerce').fillna(0).astype(int)

# Convert PolityName to integer if possible, else 0
def convert_polityname(val):
    if pd.isna(val):
        return 0
    try:
        return int(val)
    except:
        return 0

agg_df['PolityName'] = agg_df['PolityName'].apply(convert_polityname)

# Reorder columns to match target schema
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

agg_df = agg_df[target_cols]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)