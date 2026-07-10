import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)

# Join the four dimension tables on ROW_WID
dim_join_1 = pd.merge(s0, s2, on="ROW_WID", how="inner", suffixes=('_0', '_2'))
dim_join_2 = pd.merge(dim_join_1, s6, on="ROW_WID", how="inner", suffixes=('', '_6'))
dim_join_3 = pd.merge(dim_join_2, s7, on="ROW_WID", how="inner", suffixes=('', '_7'))

# Columns from dimension tables to unify (from s0, s2, s6, s7)
# For columns with suffixes, we will take first non-null value across the 4 tables
dim_cols = ['CANCELED', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP']

def first_non_null(row, cols):
    for c in cols:
        if pd.notnull(row[c]):
            return row[c]
    return None

# Prepare a DataFrame to hold unified dimension columns
dim_data = pd.DataFrame()
dim_data['ROW_WID'] = dim_join_3['ROW_WID']

# For each dimension column, gather all variants and pick first non-null
for col in dim_cols:
    variants = []
    # Possible suffixes for each source table
    # s0: no suffix or _0 (depending on merge)
    # s2: _2
    # s6: _6
    # s7: _7
    # Check which columns exist in dim_join_3
    possible_cols = []
    # s0 columns: after merges, s0 columns have no suffix or _0 (depending on merge)
    # After first merge, s0 columns have _0 suffix, after second merge, s0 columns have _0 suffix, after third merge, s0 columns have _0 suffix
    # s2 columns have _2 suffix
    # s6 columns have _6 suffix
    # s7 columns have _7 suffix
    # So variants are col+'_0', col+'_2', col+'_6', col+'_7'
    for suffix in ['_0', '_2', '_6', '_7']:
        c_name = col + suffix
        if c_name in dim_join_3.columns:
            possible_cols.append(c_name)
    # For s0 columns, also check col without suffix (in case)
    if col in dim_join_3.columns:
        possible_cols.insert(0, col)
    # Apply row-wise first non-null
    dim_data[col] = dim_join_3[possible_cols].bfill(axis=1).iloc[:, 0]

# Now join dim_data with all aspect tables on ROW_WID (left join to keep only rows present in dimension join)
df = dim_data

# Join with s1 (KEYWORDS_NUM)
df = pd.merge(df, s1, on="ROW_WID", how="left")

# Join with s3 (VISITS_NUM)
df = pd.merge(df, s3, on="ROW_WID", how="left")

# Join with s4 (COLLECTION_EVENTS_NUM)
df = pd.merge(df, s4, on="ROW_WID", how="left")

# Join with s5 (TECHSUPPORT_NUM)
df = pd.merge(df, s5, on="ROW_WID", how="left")

# Join with s8 (INBOUND_CALLS_NUM)
df = pd.merge(df, s8, on="ROW_WID", how="left")

# Join with s9 (INTERACTIONS_NUM)
df = pd.merge(df, s9, on="ROW_WID", how="left")

# Now group by ROW_WID to remove duplicates and aggregate
# Aggregation rules:
# - For dimension columns:
#   * CANCELED, ACCNT_LOC, HOME_PASSED: first (integer)
#   * ARPU, MONTHS_AGE: mean (float)
#   * SES, CUST_SINCE_DT, CANCEL_DT, CITY, POP: first (string)
# - For count columns: sum
agg_dict = {
    'CANCELED': 'first',
    'ACCNT_LOC': 'first',
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'first',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

# Some count columns may have NaN, sum will treat NaN as zero if skipna=True (default)
final_df = df.groupby('ROW_WID', as_index=False).agg(agg_dict)

# Reorder columns as per target schema
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

final_df = final_df[cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)