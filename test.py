import pandas as pd

# Load all sources according to the given file paths

# Source 0
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_0.csv', index_col=0)
# Source 1
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_1.csv', index_col=0)
# Source 2
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_2.csv', index_col=0)
# Source 3
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_3.csv', index_col=0)
# Source 4
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_4.csv', index_col=0)
# Source 5
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_5.csv', index_col=0)
# Source 6
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_6.csv', index_col=0)
# Source 7
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_7.csv', index_col=0)
# Source 8
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_8.csv', index_col=0)
# Source 9
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/test_9.csv', index_col=0)

# Step 1: Union the four main tables with the same schema
src_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED',
               'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP']

union_0 = source0[src_columns]
union_2 = source2[src_columns]
union_6 = source6[src_columns]
union_7 = source7[src_columns]

unioned_main = pd.concat([union_0, union_2, union_6, union_7], axis=0, ignore_index=True)

# Step 2: Join unioned_main with each small numeric table on ROW_WID using inner join
df = unioned_main.copy()

df = df.merge(source1, on='ROW_WID', how='inner')  # KEYWORDS_NUM
df = df.merge(source3, on='ROW_WID', how='inner')  # VISITS_NUM
df = df.merge(source4, on='ROW_WID', how='inner')  # COLLECTION_EVENTS_NUM
df = df.merge(source5, on='ROW_WID', how='inner')  # TECHSUPPORT_NUM
df = df.merge(source8, on='ROW_WID', how='inner')  # INBOUND_CALLS_NUM
df = df.merge(source9, on='ROW_WID', how='inner')  # INTERACTIONS_NUM

print("Size of Joined Data:")
print(len(df))


# Step 3: GroupBy columns chosen as per critique: 'CANCELED', 'ROW_WID', 'ACCNT_LOC'
groupby_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Step 4: Define aggregations:
agg_dict = {
    'ARPU': 'mean',               # Average float value
    'SES': 'first',               # Categorical, instance consistent within group
    'HOME_PASSED': 'first',       # Categorical/int
    'CUST_SINCE_DT': 'first',     # Date string
    'MONTHS_AGE': 'mean',         # Average float value
    'CANCEL_DT': 'first',         # Date string
    'CITY': 'first',
    'POP': 'first',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

agg_df = df.groupby(groupby_cols, as_index=False).agg(agg_dict)

# Step 5: Drop rows with any NaN values to match target dataset completeness
agg_df = agg_df.dropna()

# Step 6: Cast columns as per expected dtype to match target
agg_df['ARPU'] = pd.to_numeric(agg_df['ARPU'], errors='coerce')
agg_df['MONTHS_AGE'] = pd.to_numeric(agg_df['MONTHS_AGE'], errors='coerce')
agg_df['CANCELED'] = agg_df['CANCELED'].fillna(0).astype(int)
agg_df['HOME_PASSED'] = pd.to_numeric(agg_df['HOME_PASSED'], errors='coerce').fillna(0).astype(int)

numeric_count_cols = [
    'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM',
    'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM'
]
for col in numeric_count_cols:
    agg_df[col] = agg_df[col].astype(int)

agg_df['SES'] = agg_df['SES'].astype(str)

# Step 7: Reorder columns exactly as per target schema
target_columns = [
    'CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED',
    'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
    'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM',
    'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM'
]

agg_df = agg_df[target_columns]

# Export to the required path without index
agg_df.to_csv('autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_critique_history.csv', index=False)
