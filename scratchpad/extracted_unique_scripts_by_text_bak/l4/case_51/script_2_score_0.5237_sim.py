import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

# Align columns for union: Source1 lacks PolityName, add it with NaN
df1['PolityName'] = pd.NA

# Reorder columns to be consistent
cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
df0 = df0[cols]
df1 = df1[cols]
df2 = df2[cols]
df3 = df3[cols]

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by Side and aggregate as per partial plan
agg = df_all.groupby('Side').agg(
    WarID=('WarID', 'count'),
    Deaths=('Deaths', 'sum'),
    Outcome=('Outcome', 'max'),
    IsInitiator=('IsInitiator', 'max')
).reset_index()

# The target schema requires many more columns:
# ['Side': string, 'WarID': integer, 'PolityID': integer, 'StartYear': integer, 'StartMonth': integer, 'StartDay': integer,
#  'EndYear': integer, 'EndMonth': integer, 'EndDay': integer, 'IsInitiator': integer, 'Outcome': integer, 'Deaths': integer, 'PolityName': integer]

# The partial plan only aggregates on Side, which is insufficient to produce the full target schema.
# Instead, the target schema keys are: Side, WarID, PolityID (likely keys).
# We must group by these keys, aggregating other columns.

# So redo grouping by ['Side', 'WarID', 'PolityID'] with aggregations for other columns.

group_cols = ['Side', 'WarID', 'PolityID']

# For PolityName, it is string in source but integer in target examples (likely an ID). 
# We will try to convert PolityName to integer if possible, else leave as is.

def try_int_conversion(s):
    try:
        return int(s)
    except:
        return pd.NA

# Aggregate with appropriate functions:
agg_df = df_all.groupby(group_cols).agg(
    StartYear=('StartYear', 'max'),
    StartMonth=('StartMonth', 'max'),
    StartDay=('StartDay', 'max'),
    EndYear=('EndYear', 'max'),
    EndMonth=('EndMonth', 'max'),
    EndDay=('EndDay', 'max'),
    IsInitiator=('IsInitiator', 'max'),
    Outcome=('Outcome', 'max'),
    Deaths=('Deaths', 'sum'),
    PolityName=('PolityName', lambda x: x.dropna().iloc[0] if x.dropna().size > 0 else pd.NA)
).reset_index()

# Convert columns to integer where appropriate
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths']

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

# Reorder columns to target schema order
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']
agg_df = agg_df[target_cols]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)