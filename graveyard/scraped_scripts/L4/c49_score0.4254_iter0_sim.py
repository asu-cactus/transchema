import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_49/training_0.csv", index_col=0)

def extract_rows(df, side_col, ccode_col, start_month_col, start_day_col, start_year_col,
                 end_month_col, end_day_col, end_year_col, deaths_col):
    df_side = df[[side_col, ccode_col, 'WarNum', start_month_col, start_day_col, start_year_col,
                  end_month_col, end_day_col, end_year_col, 'Initiator', 'Outcome', deaths_col]].copy()
    df_side = df_side.rename(columns={
        side_col: 'PolityName',
        ccode_col: 'PolityID',
        'WarNum': 'WarID',
        start_month_col: 'StartMonth',
        start_day_col: 'StartDay',
        start_year_col: 'StartYear',
        end_month_col: 'EndMonth',
        end_day_col: 'EndDay',
        end_year_col: 'EndYear',
        deaths_col: 'Deaths'
    })
    # Convert PolityID to integer, fill NaN with 0 and convert
    df_side['PolityID'] = pd.to_numeric(df_side['PolityID'], errors='coerce').fillna(0).astype(int)
    # Convert WarID to int
    df_side['WarID'] = pd.to_numeric(df_side['WarID'], errors='coerce').fillna(0).astype(int)
    # Convert date columns to int, fill NaN with 0
    for col in ['StartMonth', 'StartDay', 'StartYear', 'EndMonth', 'EndDay', 'EndYear']:
        df_side[col] = pd.to_numeric(df_side[col], errors='coerce').fillna(0).astype(int)
    # Convert Initiator and Outcome to int, fill NaN with 0
    df_side['Initiator'] = pd.to_numeric(df_side['Initiator'], errors='coerce').fillna(0).astype(int)
    df_side['Outcome'] = pd.to_numeric(df_side['Outcome'], errors='coerce').fillna(0).astype(int)
    # Convert Deaths to int, fill NaN with 0
    df_side['Deaths'] = pd.to_numeric(df_side['Deaths'], errors='coerce').fillna(0).astype(int)
    # Strip whitespace from PolityName if string
    df_side['PolityName'] = df_side['PolityName'].astype(str).str.strip()
    return df_side

sideA = extract_rows(df0, 'SideA', 'CcodeA', 'StartMonth1', 'StartDay1', 'StartYear1',
                     'EndMonth1', 'EndDay1', 'EndYear1', 'SideADeaths')
sideB = extract_rows(df0, 'SideB', 'CcodeB', 'StartMonth1', 'StartDay1', 'StartYear1',
                     'EndMonth1', 'EndDay1', 'EndYear1', 'SideBDeaths')

# Some rows have second date range columns (StartMonth2 etc), extract those as well if present
sideA_2 = extract_rows(df0, 'SideA', 'CcodeA', 'StartMonth2', 'StartDay2', 'StartYear2',
                       'EndMonth2', 'EndDay2', 'EndYear2', 'SideADeaths')
sideB_2 = extract_rows(df0, 'SideB', 'CcodeB', 'StartMonth2', 'StartDay2', 'StartYear2',
                       'EndMonth2', 'EndDay2', 'EndYear2', 'SideBDeaths')

# Combine all sides
combined = pd.concat([sideA, sideB, sideA_2, sideB_2], ignore_index=True)

# Remove rows where PolityName is 'nan' or empty string after stripping
combined = combined[combined['PolityName'].notna()]
combined = combined[combined['PolityName'].str.strip() != '']

# Group by PolityName as per partial plan (though target schema includes more columns, 
# the partial plan only says GROUP_BY PolityName, so we keep all rows as is)
# The target examples show multiple rows per PolityName, so no aggregation is done here.

combined = combined[['PolityName', 'WarID', 'PolityID', 'StartMonth', 'StartDay', 'StartYear',
                     'EndMonth', 'EndDay', 'EndYear', 'Initiator', 'Outcome', 'Deaths']]

combined.to_csv("autopipeline-benchmarks/github-pipelines/length4_49/target_multisource_mcts.csv", index=False)