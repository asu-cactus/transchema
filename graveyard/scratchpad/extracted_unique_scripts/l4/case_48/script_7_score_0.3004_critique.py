import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Drop rows with NaN in key columns to avoid extra rows
key_cols = ['Initiator', 'WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Outcome']
df0 = df0.dropna(subset=key_cols)

# Group by key columns, aggregate Deaths by sum of SideADeaths
grouped = df0.groupby(key_cols, dropna=False, as_index=False)['SideADeaths'].sum()

# Rename columns to target schema
result = grouped.rename(columns={
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths'
})

# Convert columns to correct types
result['WarID'] = pd.to_numeric(result['WarID'], errors='coerce').astype('Int64')
result['PolityID'] = pd.to_numeric(result['PolityID'], errors='coerce').astype('Int64')
result['PolityName'] = pd.to_numeric(result['PolityName'], errors='coerce').astype('Int64')
result['StartMonth'] = pd.to_numeric(result['StartMonth'], errors='coerce').astype('Int64')
result['StartDay'] = pd.to_numeric(result['StartDay'], errors='coerce').astype('Int64')
result['StartYear'] = pd.to_numeric(result['StartYear'], errors='coerce').astype('Int64')
result['EndMonth'] = pd.to_numeric(result['EndMonth'], errors='coerce').astype('Int64')
result['EndDay'] = pd.to_numeric(result['EndDay'], errors='coerce').astype('Int64')
result['EndYear'] = pd.to_numeric(result['EndYear'], errors='coerce').astype('Int64')
result['Outcome'] = pd.to_numeric(result['Outcome'], errors='coerce').astype('Int64')
result['Deaths'] = pd.to_numeric(result['Deaths'], errors='coerce').fillna(0).astype('Int64')

# Reorder columns to target schema
result = result[['Initiator', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)