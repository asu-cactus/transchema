import pandas as pd

# Read all source CSVs with index_col=0 to ignore the numerical index column
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv', index_col=0)

# UNION the base tables with the same schema (columns 0-10 of target)
base_tables = [source0, source2, source4, source9]
base_union = pd.concat(base_tables, ignore_index=True)

# Join base_union with each aspect table on ROW_WID
# Use inner join to keep only matching rows (as target examples suggest)
df = base_union.merge(source1, on='ROW_WID', how='inner')
df = df.merge(source3, on='ROW_WID', how='inner')
df = df.merge(source5, on='ROW_WID', how='inner')
df = df.merge(source6, on='ROW_WID', how='inner')
df = df.merge(source7, on='ROW_WID', how='inner')
df = df.merge(source8, on='ROW_WID', how='inner')

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED',
                  'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
                  'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM',
                  'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[target_columns]

# Write to target CSV
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv', index=False)