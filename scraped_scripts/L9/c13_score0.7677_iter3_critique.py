import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_3.csv', index_col=0)
src4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_4.csv', index_col=0)
src5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_5.csv', index_col=0)
src6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_6.csv', index_col=0)
src7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_7.csv', index_col=0)
src8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_8.csv', index_col=0)
src9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_13/training_9.csv', index_col=0)

# Rename columns in each source to avoid collisions after join
# The target schema shows suffixes like _x, _y, _x_37, _y_55, etc.
# We will assign suffixes _0, _1, ..., _9 to each source to match the target columns pattern.

def rename_columns(df, suffix):
    # Except for the join keys 'Date' and 'Jour', rename all other columns by adding suffix
    # 'Chaine' is also repeated in target with suffix, so rename it too
    cols_to_rename = [col for col in df.columns if col not in ['Date', 'Jour']]
    rename_dict = {col: f"{col}_{suffix}" for col in cols_to_rename}
    return df.rename(columns=rename_dict)

src0_r = rename_columns(src0, '0')
src1_r = rename_columns(src1, '1')
src2_r = rename_columns(src2, '2')
src3_r = rename_columns(src3, '3')
src4_r = rename_columns(src4, '4')
src5_r = rename_columns(src5, '5')
src6_r = rename_columns(src6, '6')
src7_r = rename_columns(src7, '7')
src8_r = rename_columns(src8, '8')
src9_r = rename_columns(src9, '9')

# Now join all sources on ['Date', 'Jour'] using inner join
# Start with src0_r
df = src0_r

for src in [src1_r, src2_r, src3_r, src4_r, src5_r, src6_r, src7_r, src8_r, src9_r]:
    df = df.merge(src, on=['Date', 'Jour'], how='inner')

# The target schema has 'Jour_x', 'Chaine_x', etc. but we have 'Jour' and 'Chaine_0', 'Chaine_1', ...
# We need to rename 'Jour' to 'Jour_x' to match target schema's leftmost 'Jour_x'
# Also rename 'Chaine_0' to 'Chaine_x' to match target schema

df = df.rename(columns={'Jour': 'Jour_x', 'Chaine_0': 'Chaine_x'})

# The target schema has 'Date' as string, 'Jour_x' string, 'Chaine_x' string, etc.
# The 'Date' column is already string, no change needed.

# Save to target path
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_13/target_multisource_mcts.csv', index=False)