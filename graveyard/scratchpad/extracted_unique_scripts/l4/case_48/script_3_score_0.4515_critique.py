import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Helper function to create long format for a given side and period
def create_long(df, side_prefix, start_month_col, start_day_col, start_year_col, end_month_col, end_day_col, end_year_col, deaths_col):
    df_long = df[['WarNum', 'Initiator', 'Outcome',
                  f'Side{side_prefix}', f'Ccode{side_prefix}',
                  start_month_col, start_day_col, start_year_col,
                  end_month_col, end_day_col, end_year_col,
                  deaths_col]].copy()
    df_long = df_long.rename(columns={
        f'Side{side_prefix}': 'PolityName',  # will be replaced by PolityID as integer
        f'Ccode{side_prefix}': 'PolityID',
        start_month_col: 'StartMonth',
        start_day_col: 'StartDay',
        start_year_col: 'StartYear',
        end_month_col: 'EndMonth',
        end_day_col: 'EndDay',
        end_year_col: 'EndYear',
        deaths_col: 'Deaths'
    })
    # Convert types
    df_long['Initiator'] = df_long['Initiator'].astype(str)
    # PolityID and PolityName as int
    df_long['PolityID'] = pd.to_numeric(df_long['PolityID'], errors='coerce')
    # Drop rows with missing PolityID
    df_long = df_long.dropna(subset=['PolityID'])
    df_long['PolityID'] = df_long['PolityID'].astype(int)
    # PolityName is integer same as PolityID (per target schema)
    df_long['PolityName'] = df_long['PolityID']
    # Convert date and other columns to numeric, fill NaN with 0 and convert to int
    for col in ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear', 'Outcome', 'Deaths']:
        df_long[col] = pd.to_numeric(df_long[col], errors='coerce').fillna(0).astype(int)
    # WarID from WarNum
    df_long['WarID'] = df_long['WarNum'].astype(int)
    # Select columns in target order
    df_long = df_long[['Initiator', 'WarID', 'PolityID', 'PolityName',
                       'StartMonth', 'StartDay', 'StartYear',
                       'EndMonth', 'EndDay', 'EndYear',
                       'Outcome', 'Deaths']]
    return df_long

# Create four dataframes for each side and period
df_p1_a = create_long(df, 'A', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths')
df_p1_b = create_long(df, 'B', 'StartMonth1', 'StartDay1', 'StartYear1', 'EndMonth1', 'EndDay1', 'EndYear1', 'SideBDeaths')
df_p2_a = create_long(df, 'A', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'SideADeaths')
df_p2_b = create_long(df, 'B', 'StartMonth2', 'StartDay2', 'StartYear2', 'EndMonth2', 'EndDay2', 'EndYear2', 'SideBDeaths')

# Concatenate all four (UNION)
df_long = pd.concat([df_p1_a, df_p1_b, df_p2_a, df_p2_b], ignore_index=True)

# Group by all columns except Deaths, sum Deaths
group_cols = ['Initiator', 'WarID', 'PolityID', 'PolityName',
              'StartMonth', 'StartDay', 'StartYear',
              'EndMonth', 'EndDay', 'EndYear',
              'Outcome']

result = df_long.groupby(group_cols, as_index=False).agg({'Deaths': 'sum'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)