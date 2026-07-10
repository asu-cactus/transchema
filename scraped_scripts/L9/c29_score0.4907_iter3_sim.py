import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

# Union the three sources with identical schema (the large 11-column tables)
df_234569 = pd.concat([df2, df5, df6, df9], ignore_index=True)

# Merge all single-metric tables on ROW_WID
df_single_metrics = df0[['ROW_WID', 'COLLECTION_EVENTS_NUM']].merge(
    df1[['ROW_WID', 'VISITS_NUM']], on='ROW_WID', how='outer').merge(
    df3[['ROW_WID', 'INBOUND_CALLS_NUM']], on='ROW_WID', how='outer').merge(
    df4[['ROW_WID', 'KEYWORDS_NUM']], on='ROW_WID', how='outer').merge(
    df7[['ROW_WID', 'INTERACTIONS_NUM']], on='ROW_WID', how='outer').merge(
    df8[['ROW_WID', 'TECHSUPPORT_NUM']], on='ROW_WID', how='outer')

# Merge the big table with the single metrics on ROW_WID
df_merged = df_234569.merge(df_single_metrics, on='ROW_WID', how='outer')

# Select all columns except ROW_WID and CANCELED, ACCNT_LOC, ARPU, SES, HOME_PASSED, CUST_SINCE_DT, MONTHS_AGE, CANCEL_DT, CITY, POP
# Because target only has COLLECTION_EVENTS_NUM, we only keep COLLECTION_EVENTS_NUM column from all sources

# Unpivot all numeric *_NUM columns except COLLECTION_EVENTS_NUM to rows, then group by COLLECTION_EVENTS_NUM

# Identify all columns ending with _NUM except COLLECTION_EVENTS_NUM
num_cols = [col for col in df_merged.columns if col.endswith('_NUM') and col != 'COLLECTION_EVENTS_NUM']

# Prepare DataFrame for unpivot: keep ROW_WID and all *_NUM columns except COLLECTION_EVENTS_NUM
df_unpivot = df_merged[['ROW_WID', 'COLLECTION_EVENTS_NUM'] + num_cols]

# Melt all *_NUM columns except COLLECTION_EVENTS_NUM into one column
melted = df_unpivot.melt(id_vars=['ROW_WID', 'COLLECTION_EVENTS_NUM'], value_vars=num_cols,
                         var_name='metric', value_name='value')

# Combine COLLECTION_EVENTS_NUM and the melted values into one series for grouping
# We want to count occurrences of each COLLECTION_EVENTS_NUM value plus the values in other *_NUM columns

# Create a series of COLLECTION_EVENTS_NUM values (dropping NaNs)
col_events = df_unpivot['COLLECTION_EVENTS_NUM'].dropna()

# Create a series of all other numeric values from melted (dropping NaNs)
other_values = melted['value'].dropna()

# Concatenate these two series
all_values = pd.concat([col_events, other_values])

# Group by the values and count occurrences
result = all_values.value_counts().reset_index()
result.columns = ['COLLECTION_EVENTS_NUM', 'count']

# The target schema only has COLLECTION_EVENTS_NUM column, so we keep unique values only
# The target examples show only COLLECTION_EVENTS_NUM column, so we output unique values (not counts)
# So final output is unique COLLECTION_EVENTS_NUM values from all numeric columns combined

final = pd.DataFrame({'COLLECTION_EVENTS_NUM': all_values.dropna().astype(int).unique()})
final = final.sort_values('COLLECTION_EVENTS_NUM').reset_index(drop=True)

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)