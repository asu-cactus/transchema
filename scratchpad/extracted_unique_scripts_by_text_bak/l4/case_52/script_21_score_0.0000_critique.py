import pandas as pd

# Read sources with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv', index_col=0)

# Source3 lacks PolityName column, add it with NaNs to match schema
source3['PolityName'] = pd.NA

# Ensure all sources have the same columns in the same order as target schema (except IsInitiator is first)
# Source columns: ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
# Target schema order: ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

# Reorder columns for each source to match target schema order (except PolityName is last)
def reorder_cols(df):
    cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']
    # Some sources may have columns as float, convert to appropriate types later
    # For now, just reorder and keep as is
    return df[cols]

source0 = reorder_cols(source0)
source1 = reorder_cols(source1)
source2 = reorder_cols(source2)
source3 = reorder_cols(source3)

# UNION all sources
df_all = pd.concat([source0, source1, source2, source3], ignore_index=True)

# Group by leftmost columns (non-float, likely unique identifiers)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay']

# Aggregations:
# - Deaths: sum
# - EndYear, EndMonth, EndDay, Side, Outcome, PolityName: take first non-null value
agg_dict = {
    'Deaths': 'sum',
    'EndYear': 'first',
    'EndMonth': 'first',
    'EndDay': 'first',
    'Side': 'first',
    'Outcome': 'first',
    'PolityName': 'first'
}

df_grouped = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# After aggregation, reorder columns to target schema order
final_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
              'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

df_final = df_grouped[final_cols]

# Fill NaNs with 0 for integer columns before converting
# PolityName is string in source, but target schema says integer - we keep as is (string) because no info on encoding
# So convert all columns except PolityName to int, PolityName keep as string (or fillna with empty string)
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths']

df_final[int_cols] = df_final[int_cols].fillna(0).astype(int)

# For PolityName, fill NaN with empty string (or keep as is)
df_final['PolityName'] = df_final['PolityName'].fillna('')

# Write to CSV
df_final.to_csv('autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv', index=False)