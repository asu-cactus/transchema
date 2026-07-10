import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

# Convert numeric columns, coercing errors to NaN
for col in ['SideADeaths', 'SideBDeaths',
            'StartYear1', 'StartMonth1', 'StartDay1',
            'EndYear1', 'EndMonth1', 'EndDay1',
            'StartYear2', 'StartMonth2', 'StartDay2',
            'EndYear2', 'EndMonth2', 'EndDay2',
            'CcodeA', 'Outcome']:
    df0[col] = pd.to_numeric(df0[col], errors='coerce')

# Fill NaN deaths with 0 and convert to int
df0['SideADeaths'] = df0['SideADeaths'].fillna(0).astype(int)
df0['SideBDeaths'] = df0['SideBDeaths'].fillna(0).astype(int)

# Fill NaN in CcodeA with 0 and convert to int
df0['CcodeA'] = df0['CcodeA'].fillna(0).astype(int)

# Define aggregation functions
def first_non_null(series):
    return series.dropna().iloc[0] if not series.dropna().empty else np.nan

def mode_or_nan(series):
    modes = series.mode()
    if modes.empty:
        return np.nan
    else:
        return modes.iloc[0]

agg_dict = {
    'SideA': first_non_null,
    'StartYear1': 'min',
    'StartMonth1': 'min',
    'StartDay1': 'min',
    'StartYear2': 'min',
    'StartMonth2': 'min',
    'StartDay2': 'min',
    'EndYear1': 'max',
    'EndMonth1': 'max',
    'EndDay1': 'max',
    'EndYear2': 'max',
    'EndMonth2': 'max',
    'EndDay2': 'max',
    'Initiator': first_non_null,
    'Outcome': mode_or_nan,
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum'
}

grouped = df0.groupby(['WarNum', 'CcodeA'], as_index=False).agg(agg_dict)

# Compute earliest start date from two start dates
def earliest_start(row):
    # Create tuples for start dates if year is valid (>0)
    dates = []
    if pd.notna(row['StartYear1']) and row['StartYear1'] > 0:
        dates.append((int(row['StartYear1']),
                      int(row['StartMonth1']) if pd.notna(row['StartMonth1']) else 1,
                      int(row['StartDay1']) if pd.notna(row['StartDay1']) else 1))
    if pd.notna(row['StartYear2']) and row['StartYear2'] > 0:
        dates.append((int(row['StartYear2']),
                      int(row['StartMonth2']) if pd.notna(row['StartMonth2']) else 1,
                      int(row['StartDay2']) if pd.notna(row['StartDay2']) else 1))
    if not dates:
        return (1,1,1)  # default minimal date
    return min(dates)

# Compute latest end date from two end dates
def latest_end(row):
    dates = []
    if pd.notna(row['EndYear1']) and row['EndYear1'] > 0:
        dates.append((int(row['EndYear1']),
                      int(row['EndMonth1']) if pd.notna(row['EndMonth1']) else 1,
                      int(row['EndDay1']) if pd.notna(row['EndDay1']) else 1))
    if pd.notna(row['EndYear2']) and row['EndYear2'] > 0:
        dates.append((int(row['EndYear2']),
                      int(row['EndMonth2']) if pd.notna(row['EndMonth2']) else 1,
                      int(row['EndDay2']) if pd.notna(row['EndDay2']) else 1))
    if not dates:
        return (1,1,1)  # default minimal date
    return max(dates)

start_dates = grouped.apply(earliest_start, axis=1)
end_dates = grouped.apply(latest_end, axis=1)

grouped['StartYear'] = start_dates.apply(lambda x: x[0])
grouped['StartMonth'] = start_dates.apply(lambda x: x[1])
grouped['StartDay'] = start_dates.apply(lambda x: x[2])

grouped['EndYear'] = end_dates.apply(lambda x: x[0])
grouped['EndMonth'] = end_dates.apply(lambda x: x[1])
grouped['EndDay'] = end_dates.apply(lambda x: x[2])

# Sum deaths
grouped['Deaths'] = grouped['SideADeaths'] + grouped['SideBDeaths']

# Factorize Initiator to integer codes, preserving NaN as is
initiator_codes, uniques = pd.factorize(grouped['Initiator'])
# Replace -1 (for NaN) with np.nan
grouped['Initiator'] = initiator_codes
grouped.loc[initiator_codes == -1, 'Initiator'] = np.nan
grouped['Initiator'] = grouped['Initiator'].astype('Int64')  # nullable integer dtype

# Outcome is numeric, convert to Int64 nullable
grouped['Outcome'] = grouped['Outcome'].astype('Int64')

# PolityName is SideA (string)
grouped['PolityName'] = grouped['SideA']

# Rename columns to target schema
grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID'
}, inplace=True)

# Select and order columns as per target schema
cols = ['PolityName', 'WarID', 'PolityID',
        'StartMonth', 'StartDay', 'StartYear',
        'EndMonth', 'EndDay', 'EndYear',
        'Initiator', 'Outcome', 'Deaths']

result = grouped[cols]

# Write output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)