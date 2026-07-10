import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv", index_col=0)

# Join dimension tables on ROW_WID
df = s2.merge(s3, on="ROW_WID", how="inner", suffixes=('_2', '_3'))
df = df.merge(s4, on="ROW_WID", how="inner", suffixes=('', '_4'))
df = df.merge(s9, on="ROW_WID", how="inner", suffixes=('', '_9'))

# After merges, columns from s3, s4, s9 with suffixes may exist, but schemas are identical.
# We only want one set of dimension columns, so drop duplicates from suffixes.
# Since all dimension tables have same columns, keep columns from s2 and drop duplicates from others.

# To avoid duplicated columns, keep columns from s2 and s9 only once:
# Actually, since all dimension tables have same columns, after merge, columns from s3, s4, s9 will be duplicated.
# We can keep columns from s2 and s9 only, or just from s2 and drop duplicates.

# But since s9 has some different values, better to keep s2 columns and drop duplicates from s3, s4, s9.

# Let's keep columns from s2 and s9 only, drop columns with suffixes _3, _4, _9 except ROW_WID.

cols_to_drop = [col for col in df.columns if col.endswith('_2') or col.endswith('_3') or col.endswith('_4') or col.endswith('_9')]
# But s2 columns have no suffix, s3 columns have _3, s4 columns have _4, s9 columns have _9
# s2 columns have no suffix, so no need to drop those.
# Actually, s2 columns have no suffix, s3 columns have _3, s4 columns have _4, s9 columns have _9
# So drop columns with suffixes _3 and _4, keep s2 and s9 columns.

cols_to_drop = [col for col in df.columns if col.endswith('_3') or col.endswith('_4')]

df = df.drop(columns=cols_to_drop)

# Now join with aspect tables on ROW_WID
df = df.merge(s0, on="ROW_WID", how="inner")
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s5, on="ROW_WID", how="inner")
df = df.merge(s6, on="ROW_WID", how="inner")
df = df.merge(s7, on="ROW_WID", how="inner")
df = df.merge(s8, on="ROW_WID", how="inner")

# Select columns as per target schema
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)