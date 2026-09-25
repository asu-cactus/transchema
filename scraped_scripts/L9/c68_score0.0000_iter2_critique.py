import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

# Join dimension tables on ROW_WID
df = s0.merge(s2, on="ROW_WID", how="inner", suffixes=('_0', '_2'))
df = df.merge(s4, on="ROW_WID", how="inner", suffixes=('', '_4'))
df = df.merge(s9, on="ROW_WID", how="inner", suffixes=('', '_9'))

# After these merges, columns from s0, s2, s4, s9 are duplicated with suffixes.
# We need to select columns from one dimension table only (e.g., s0) because target schema has only one set of dimension columns.
# The dimension tables have the same schema, so we can pick columns from s0 (or any one) and ignore duplicates from others.

# To avoid confusion, let's just use s0 columns for dimension columns and ignore duplicates from s2, s4, s9.
# So, drop duplicated dimension columns from s2, s4, s9 (those with suffixes).

# Identify dimension columns (all except ROW_WID)
dim_cols = ['CANCELED', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP']

# Keep only s0 dimension columns and ROW_WID, drop others with suffixes
cols_to_keep = ['ROW_WID'] + dim_cols
df = df[cols_to_keep]

# Join aspect tables on ROW_WID
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s3, on="ROW_WID", how="inner")
df = df.merge(s5, on="ROW_WID", how="inner")
df = df.merge(s6, on="ROW_WID", how="inner")
df = df.merge(s7, on="ROW_WID", how="inner")
df = df.merge(s8, on="ROW_WID", how="inner")

# Final projection to match target schema column order
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)