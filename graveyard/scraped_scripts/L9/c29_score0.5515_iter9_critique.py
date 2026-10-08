import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_4.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_8.csv", index_col=0)

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

# UNION dimension tables (all have ROW_WID and many columns)
unioned_dim = pd.concat([s2, s5, s6, s9], ignore_index=True)

# Prepare aspect tables: rename their numeric column to COLLECTION_EVENTS_NUM
def prepare_aspect(df):
    id_col = 'ROW_WID'
    val_col = [c for c in df.columns if c != id_col][0]
    return df.rename(columns={val_col: 'COLLECTION_EVENTS_NUM'})[['ROW_WID', 'COLLECTION_EVENTS_NUM']]

a0 = prepare_aspect(s0)
a1 = prepare_aspect(s1)
a3 = prepare_aspect(s3)
a4 = prepare_aspect(s4)
a7 = prepare_aspect(s7)
a8 = prepare_aspect(s8)

# Join all aspect tables to unioned_dim on ROW_WID
df = unioned_dim[['ROW_WID']].drop_duplicates()

for aspect in [a0, a1, a3, a4, a7, a8]:
    df = df.merge(aspect, on='ROW_WID', how='left', suffixes=('', '_dup'))
    # If suffix added, drop duplicate column
    dup_cols = [c for c in df.columns if c.endswith('_dup')]
    if dup_cols:
        df.drop(columns=dup_cols, inplace=True)

# Fill NaN in COLLECTION_EVENTS_NUM columns with 0
# There are multiple COLLECTION_EVENTS_NUM columns from each join, but all have same name,
# so after merge, only one COLLECTION_EVENTS_NUM column exists, overwritten each time.
# To avoid overwriting, rename COLLECTION_EVENTS_NUM before merge.

# So we need to rename COLLECTION_EVENTS_NUM in each aspect table before merge to unique names:
# Let's redo the join with unique names:

df = unioned_dim[['ROW_WID']].drop_duplicates()

aspect_dfs = {
    'COLLECTION_EVENTS_NUM_0': a0,
    'COLLECTION_EVENTS_NUM_1': a1,
    'COLLECTION_EVENTS_NUM_3': a3,
    'COLLECTION_EVENTS_NUM_4': a4,
    'COLLECTION_EVENTS_NUM_7': a7,
    'COLLECTION_EVENTS_NUM_8': a8,
}

for colname, aspect in aspect_dfs.items():
    aspect_renamed = aspect.rename(columns={'COLLECTION_EVENTS_NUM': colname})
    df = df.merge(aspect_renamed, on='ROW_WID', how='left')

# Fill NaN with 0
df = df.fillna(0)

# Sum all COLLECTION_EVENTS_NUM_* columns to get final COLLECTION_EVENTS_NUM
df['COLLECTION_EVENTS_NUM'] = df[list(aspect_dfs.keys())].sum(axis=1).astype(int)

# Project only COLLECTION_EVENTS_NUM as target schema
result = df[['COLLECTION_EVENTS_NUM']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)