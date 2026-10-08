import pandas as pd

sideA_path = "autopipeline-benchmarks/github-pipelines/length4_50/training_0_sideA.csv"
sideB_path = "autopipeline-benchmarks/github-pipelines/length4_50/training_0_sideB.csv"

df_sideA = pd.read_csv(sideA_path, index_col=0)
df_sideB = pd.read_csv(sideB_path, index_col=0)

# Extract sideA relevant columns and rename to target schema
df_sideA_extracted = df_sideA.rename(columns={
    'Outcome': 'Outcome',
    'WarNum': 'WarID',
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'Initiator': 'Initiator',
    'SideADeaths': 'Deaths'
})[
    ['Outcome', 'WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1',
     'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'SideADeaths']
].rename(columns={
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

# Extract sideB relevant columns and rename to target schema
df_sideB_extracted = df_sideB.rename(columns={
    'Outcome': 'Outcome',
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'Initiator': 'Initiator',
    'SideBDeaths': 'Deaths'
})[
    ['Outcome', 'WarNum', 'CcodeB', 'SideB', 'StartMonth1', 'StartDay1', 'StartYear1',
     'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'SideBDeaths']
].rename(columns={
    'WarNum': 'WarID',
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideBDeaths': 'Deaths'
})

# Concatenate sideA and sideB extracted data
df = pd.concat([df_sideA_extracted, df_sideB_extracted], ignore_index=True)

# Convert columns to appropriate types
for col in ['Outcome', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Deaths']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# PolityName is string, keep as is (no conversion to int)
# Strip whitespace and standardize PolityName strings if needed
df['PolityName'] = df['PolityName'].astype(str).str.strip()

# Group by all columns except Deaths and sum Deaths
group_by_cols = ['Outcome', 'WarID', 'PolityID', 'PolityName', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator']
df = df.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Write to output
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_50/target_multisource_mcts.csv", index=False)