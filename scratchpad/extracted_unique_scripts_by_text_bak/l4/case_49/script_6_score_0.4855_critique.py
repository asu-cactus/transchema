import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv"
df = pd.read_csv(src0_path, index_col=0)

# Prepare left side data (Side A)
df_left = df[['WarNum', 'CcodeA', 'SideA', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'Initiator', 'Outcome', 'SideADeaths']].copy()
df_left.rename(columns={
    'CcodeA': 'PolityID',
    'SideA': 'PolityName',
    'StartMonth1': 'StartMonth',
    'StartDay1': 'StartDay',
    'StartYear1': 'StartYear',
    'EndMonth1': 'EndMonth',
    'EndDay1': 'EndDay',
    'EndYear1': 'EndYear',
    'SideADeaths': 'Deaths',
    'WarNum': 'WarID'
}, inplace=True)

# Prepare right side data (Side B)
df_right = df[['WarNum', 'CcodeB', 'SideB', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'Initiator', 'Outcome', 'SideBDeaths']].copy()
df_right.rename(columns={
    'CcodeB': 'PolityID',
    'SideB': 'PolityName',
    'StartMonth2': 'StartMonth',
    'StartDay2': 'StartDay',
    'StartYear2': 'StartYear',
    'EndMonth2': 'EndMonth',
    'EndDay2': 'EndDay',
    'EndYear2': 'EndYear',
    'SideBDeaths': 'Deaths',
    'WarNum': 'WarID'
}, inplace=True)

# Convert columns to appropriate types and fill missing values with 0 for numeric columns
for df_side in [df_left, df_right]:
    df_side['PolityName'] = df_side['PolityName'].astype(str)
    df_side['PolityID'] = pd.to_numeric(df_side['PolityID'], errors='coerce').fillna(0).astype('Int64')
    df_side['StartMonth'] = pd.to_numeric(df_side['StartMonth'], errors='coerce').fillna(0).astype('Int64')
    df_side['StartDay'] = pd.to_numeric(df_side['StartDay'], errors='coerce').fillna(0).astype('Int64')
    df_side['StartYear'] = pd.to_numeric(df_side['StartYear'], errors='coerce').fillna(0).astype('Int64')
    df_side['EndMonth'] = pd.to_numeric(df_side['EndMonth'], errors='coerce').fillna(0).astype('Int64')
    df_side['EndDay'] = pd.to_numeric(df_side['EndDay'], errors='coerce').fillna(0).astype('Int64')
    df_side['EndYear'] = pd.to_numeric(df_side['EndYear'], errors='coerce').fillna(0).astype('Int64')
    df_side['Initiator'] = pd.to_numeric(df_side['Initiator'], errors='coerce').fillna(0).astype('Int64')
    df_side['Outcome'] = pd.to_numeric(df_side['Outcome'], errors='coerce').fillna(0).astype('Int64')
    df_side['Deaths'] = pd.to_numeric(df_side['Deaths'], errors='coerce').fillna(0).astype('Int64')
    df_side['WarID'] = pd.to_numeric(df_side['WarID'], errors='coerce').astype('Int64')

# Concatenate both sides (UNION)
df_all = pd.concat([df_left, df_right], ignore_index=True)

# Drop rows with missing PolityName or empty strings (if any)
df_all = df_all[df_all['PolityName'].str.strip() != '']
df_all = df_all.dropna(subset=['PolityName'])

# Group by all key columns except Deaths, sum Deaths
group_by_cols = ['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome']
df_final = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg({'Deaths': 'sum'})

# Ensure column order matches target schema exactly
df_final = df_final[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)