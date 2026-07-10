import pandas as pd

# Read source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Helper functions to choose start and end dates (prefer first period if available)
def choose_start_month(row):
    if pd.notna(row['StartMonth1']):
        return int(row['StartMonth1'])
    elif pd.notna(row['StartMonth2']):
        return int(row['StartMonth2'])
    else:
        return pd.NA

def choose_start_day(row):
    if pd.notna(row['StartDay1']):
        return int(row['StartDay1'])
    elif pd.notna(row['StartDay2']):
        return int(row['StartDay2'])
    else:
        return pd.NA

def choose_start_year(row):
    if pd.notna(row['StartYear1']):
        return int(row['StartYear1'])
    elif pd.notna(row['StartYear2']):
        return int(row['StartYear2'])
    else:
        return pd.NA

def choose_end_month(row):
    if pd.notna(row['EndMonth1']):
        return int(row['EndMonth1'])
    elif pd.notna(row['EndMonth2']):
        return int(row['EndMonth2'])
    else:
        return pd.NA

def choose_end_day(row):
    if pd.notna(row['EndDay1']):
        return int(row['EndDay1'])
    elif pd.notna(row['EndDay2']):
        return int(row['EndDay2'])
    else:
        return pd.NA

def choose_end_year(row):
    if pd.notna(row['EndYear1']):
        return int(row['EndYear1'])
    elif pd.notna(row['EndYear2']):
        return int(row['EndYear2'])
    else:
        return pd.NA

# Prepare side A dataframe
df_A = pd.DataFrame({
    'Initiator': df['Initiator'],
    'WarID': df['WarNum'].astype('Int64'),
    'PolityID': df['CcodeA'].astype('Int64'),
    'PolityName': df['CcodeA'].astype('Int64'),  # PolityName same as PolityID (integer)
    'StartMonth': df.apply(choose_start_month, axis=1),
    'StartDay': df.apply(choose_start_day, axis=1),
    'StartYear': df.apply(choose_start_year, axis=1),
    'EndMonth': df.apply(choose_end_month, axis=1),
    'EndDay': df.apply(choose_end_day, axis=1),
    'EndYear': df.apply(choose_end_year, axis=1),
    'Outcome': df['Outcome'].astype('Int64'),
    'Deaths': df['SideADeaths'].fillna(0).astype('Int64')
})

# Prepare side B dataframe
df_B = pd.DataFrame({
    'Initiator': df['Initiator'],
    'WarID': df['WarNum'].astype('Int64'),
    'PolityID': df['CcodeB'].astype('Int64'),
    'PolityName': df['CcodeB'].astype('Int64'),  # PolityName same as PolityID (integer)
    'StartMonth': df.apply(choose_start_month, axis=1),
    'StartDay': df.apply(choose_start_day, axis=1),
    'StartYear': df.apply(choose_start_year, axis=1),
    'EndMonth': df.apply(choose_end_month, axis=1),
    'EndDay': df.apply(choose_end_day, axis=1),
    'EndYear': df.apply(choose_end_year, axis=1),
    'Outcome': df['Outcome'].astype('Int64'),
    'Deaths': df['SideBDeaths'].fillna(0).astype('Int64')
})

# Remove rows where PolityID is NA (no polity on that side)
df_A = df_A[df_A['PolityID'].notna()]
df_B = df_B[df_B['PolityID'].notna()]

# Union side A and side B dataframes
df_union = pd.concat([df_A, df_B], ignore_index=True)

# Group by all identifying columns except Deaths, sum Deaths
group_by_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear',
                 'EndMonth', 'EndDay', 'EndYear', 'Outcome']

df_result = df_union.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Convert columns to correct types (Initiator string, others int)
df_result['Initiator'] = df_result['Initiator'].astype(str)
for col in group_by_cols[1:]:  # all except Initiator
    df_result[col] = df_result[col].astype('Int64')
df_result['Deaths'] = df_result['Deaths'].astype('Int64')

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)