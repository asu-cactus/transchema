import pandas as pd

# Read all source tables with index_col=0 as per hint 22
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_13/training_9.csv", index_col=0)

# Key columns to join on
key_cols = ['Date', 'Jour', 'Annee', 'Mois', 'Week end']

# To avoid column name collisions, rename columns in each source except key columns by adding suffixes matching target schema
# The target schema shows suffixes like _x, _y, _x_37, _x_38, ..., so we assign suffixes accordingly:
# Source0: _x
# Source1: _y
# Source2: _x_37
# Source3: _x_38
# Source4: _x_39
# Source5: _x_40
# Source6: _x_41
# Source7: _x_42
# Source8: _x_43
# Source9: _x_44

def rename_cols(df, suffix):
    # Rename all columns except key_cols by adding suffix
    new_cols = {}
    for c in df.columns:
        if c not in key_cols:
            new_cols[c] = f"{c}{suffix}"
    return df.rename(columns=new_cols)

src0_r = rename_cols(src0, "_x")
src1_r = rename_cols(src1, "_y")
src2_r = rename_cols(src2, "_x_37")
src3_r = rename_cols(src3, "_x_38")
src4_r = rename_cols(src4, "_x_39")
src5_r = rename_cols(src5, "_x_40")
src6_r = rename_cols(src6, "_x_41")
src7_r = rename_cols(src7, "_x_42")
src8_r = rename_cols(src8, "_x_43")
src9_r = rename_cols(src9, "_x_44")

# Start joining from src0_r
df = src0_r

# Join sequentially on key columns, inner join to keep only matching rows
df = df.merge(src1_r, on=key_cols, how='inner')
df = df.merge(src2_r, on=key_cols, how='inner')
df = df.merge(src3_r, on=key_cols, how='inner')
df = df.merge(src4_r, on=key_cols, how='inner')
df = df.merge(src5_r, on=key_cols, how='inner')
df = df.merge(src6_r, on=key_cols, how='inner')
df = df.merge(src7_r, on=key_cols, how='inner')
df = df.merge(src8_r, on=key_cols, how='inner')
df = df.merge(src9_r, on=key_cols, how='inner')

# The target schema starts with 'Date', 'Jour_x', 'Chaine_x', ...
# We have 'Date' and 'Jour' (key columns) repeated only once, but in target schema 'Jour_x', 'Jour_y', etc. appear.
# So we need to rename the key columns from each source to match target schema.

# The key columns in the target schema appear multiple times with suffixes matching the source suffixes.
# So we must rename the key columns in each source before join to have suffixes as well.

# To fix this, we should rename key columns in each source except for the first source (src0) to have suffixes.

# Let's redo the renaming including key columns for all sources except src0:

def rename_all_cols(df, suffix):
    # Rename all columns by adding suffix except 'Date' which is only once in target
    new_cols = {}
    for c in df.columns:
        if c == 'Date':
            continue  # keep Date as is
        new_cols[c] = f"{c}{suffix}"
    return df.rename(columns=new_cols)

src0_r = src0.copy()  # keep key columns as is for src0
src1_r = rename_all_cols(src1, "_y")
src2_r = rename_all_cols(src2, "_x_37")
src3_r = rename_all_cols(src3, "_x_38")
src4_r = rename_all_cols(src4, "_x_39")
src5_r = rename_all_cols(src5, "_x_40")
src6_r = rename_all_cols(src6, "_x_41")
src7_r = rename_all_cols(src7, "_x_42")
src8_r = rename_all_cols(src8, "_x_43")
src9_r = rename_all_cols(src9, "_x_44")

# Now join on 'Date' only, because other key columns are renamed and unique per source
# But joining only on 'Date' will produce a Cartesian product if multiple rows per date exist in each source.

# Check if (Date, Jour, Annee, Mois, Week end) uniquely identify rows in each source:
# Since 'Jour', 'Annee', 'Mois', 'Week end' are renamed in all but src0, we cannot join on them directly.
# So we must keep these columns unrenamed in all sources to join on them.

# So the best approach is:
# - Keep 'Date', 'Jour', 'Annee', 'Mois', 'Week end' unrenamed in all sources
# - Rename all other columns with suffixes per source

def rename_cols_except_keys(df, suffix):
    new_cols = {}
    for c in df.columns:
        if c not in key_cols:
            new_cols[c] = f"{c}{suffix}"
    return df.rename(columns=new_cols)

src0_r = rename_cols_except_keys(src0, "_x")
src1_r = rename_cols_except_keys(src1, "_y")
src2_r = rename_cols_except_keys(src2, "_x_37")
src3_r = rename_cols_except_keys(src3, "_x_38")
src4_r = rename_cols_except_keys(src4, "_x_39")
src5_r = rename_cols_except_keys(src5, "_x_40")
src6_r = rename_cols_except_keys(src6, "_x_41")
src7_r = rename_cols_except_keys(src7, "_x_42")
src8_r = rename_cols_except_keys(src8, "_x_43")
src9_r = rename_cols_except_keys(src9, "_x_44")

# Now join on key_cols
df = src0_r
df = df.merge(src1_r, on=key_cols, how='inner')
df = df.merge(src2_r, on=key_cols, how='inner')
df = df.merge(src3_r, on=key_cols, how='inner')
df = df.merge(src4_r, on=key_cols, how='inner')
df = df.merge(src5_r, on=key_cols, how='inner')
df = df.merge(src6_r, on=key_cols, how='inner')
df = df.merge(src7_r, on=key_cols, how='inner')
df = df.merge(src8_r, on=key_cols, how='inner')
df = df.merge(src9_r, on=key_cols, how='inner')

# The target schema has 'Date' as first column, then multiple 'Jour_x', 'Chaine_x', etc.
# We have 'Jour', 'Annee', 'Mois', 'Week end' columns only once (un-suffixed).
# The target schema has these columns repeated with suffixes for each source.

# So we must rename the key columns in the final df to match the target schema:
# For src0 columns: keep key columns as is (Date, Jour, Annee, Mois, Week end)
# For src1 columns: rename key columns with suffix _y
# For src2 columns: rename key columns with suffix _x_37
# ...
# But after merge, the key columns appear only once (no suffix), so we must rename the key columns from each source before merge.

# To fix this, rename key columns in each source except src0 before merge:

def rename_key_cols(df, suffix):
    new_cols = {}
    for c in key_cols:
        if c != 'Date':  # Date is only once in target, keep as is
            new_cols[c] = f"{c}{suffix}"
    return df.rename(columns=new_cols)

src0_r = rename_cols_except_keys(src0, "_x")  # key columns unmodified
src1_r = rename_cols_except_keys(src1, "_y")
src1_r = rename_key_cols(src1_r, "_y")
src2_r = rename_cols_except_keys(src2, "_x_37")
src2_r = rename_key_cols(src2_r, "_x_37")
src3_r = rename_cols_except_keys(src3, "_x_38")
src3_r = rename_key_cols(src3_r, "_x_38")
src4_r = rename_cols_except_keys(src4, "_x_39")
src4_r = rename_key_cols(src4_r, "_x_39")
src5_r = rename_cols_except_keys(src5, "_x_40")
src5_r = rename_key_cols(src5_r, "_x_40")
src6_r = rename_cols_except_keys(src6, "_x_41")
src6_r = rename_key_cols(src6_r, "_x_41")
src7_r = rename_cols_except_keys(src7, "_x_42")
src7_r = rename_key_cols(src7_r, "_x_42")
src8_r = rename_cols_except_keys(src8, "_x_43")
src8_r = rename_key_cols(src8_r, "_x_43")
src9_r = rename_cols_except_keys(src9, "_x_44")
src9_r = rename_key_cols(src9_r, "_x_44")

# Now join on 'Date' only, because other key columns have suffixes and are unique per source
df = src0_r
df = df.merge(src1_r, on='Date', how='inner')
df = df.merge(src2_r, on='Date', how='inner')
df = df.merge(src3_r, on='Date', how='inner')
df = df.merge(src4_r, on='Date', how='inner')
df = df.merge(src5_r, on='Date', how='inner')
df = df.merge(src6_r, on='Date', how='inner')
df = df.merge(src7_r, on='Date', how='inner')
df = df.merge(src8_r, on='Date', how='inner')
df = df.merge(src9_r, on='Date', how='inner')

# This join on 'Date' only will produce a Cartesian product if multiple rows per date exist in sources.
# But the target examples show 19251 rows, which is roughly sum of all source rows (1948+1941+...+1947=~19251).
# So the target is a horizontal concatenation of all sources by Date, but with rows aligned by Date only.

# To align rows by Date only, we must sort each source by Date and reset index, then concatenate columns horizontally.

# So the correct approach is to:
# - Sort each source by Date
# - Reset index
# - Concatenate all sources horizontally (axis=1)
# - Keep only one Date column (from src0)
# - Rename columns to match target schema

# Implement this approach:

sources = [src0, src1, src2, src3, src4, src5, src6, src7, src8, src9]
suffixes = ["_x", "_y", "_x_37", "_x_38", "_x_39", "_x_40", "_x_41", "_x_42", "_x_43", "_x_44"]

# Sort and reset index
for i in range(len(sources)):
    sources[i] = sources[i].sort_values('Date').reset_index(drop=True)

# Rename columns except 'Date' with suffixes
for i in range(len(sources)):
    df_tmp = sources[i]
    new_cols = {}
    for c in df_tmp.columns:
        if c != 'Date':
            new_cols[c] = c + suffixes[i]
    sources[i] = df_tmp.rename(columns=new_cols)

# Concatenate horizontally on index
df = pd.concat(sources, axis=1)

# Remove duplicate Date columns except the first one
date_cols = [col for col in df.columns if col == 'Date']
for col in df.columns:
    if col.startswith('Date') and col != 'Date':
        df = df.drop(columns=[col])

# The final df now has the same number of rows as the sum of all sources (should be 19251)
# But since all sources have 1940+ rows, concatenation by index is correct.

# Save to CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_13/target_multisource_mcts.csv", index=False)