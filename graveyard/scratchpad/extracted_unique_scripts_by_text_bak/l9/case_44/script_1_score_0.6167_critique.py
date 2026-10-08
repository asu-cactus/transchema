import pandas as pd

# Read all source tables with index_col=0 to ignore the numerical index column
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_44/training_9.csv', index_col=0)

# We want to join these 10 tables on 'Baker' column.
# Each source has columns: ['Baker', '1', '2', ..., '10', 'season']
# The target has columns: ['Baker', '1', '2', ..., '10', 'season']
# But the target columns '1' through '10' correspond to the columns '1' from each source table respectively.
# So we need to rename columns '1' in each source to the corresponding target column name.

# Rename the '1' column in each source to the corresponding target column name (from '1' to '10')
source0_renamed = source0[['Baker', '1', 'season']].rename(columns={'1': '1'})
source1_renamed = source1[['Baker', '1']].rename(columns={'1': '2'})
source2_renamed = source2[['Baker', '1']].rename(columns={'1': '3'})
source3_renamed = source3[['Baker', '1']].rename(columns={'1': '4'})
source4_renamed = source4[['Baker', '1']].rename(columns={'1': '5'})
source5_renamed = source5[['Baker', '1']].rename(columns={'1': '6'})
source6_renamed = source6[['Baker', '1']].rename(columns={'1': '7'})
source7_renamed = source7[['Baker', '1']].rename(columns={'1': '8'})
source8_renamed = source8[['Baker', '1']].rename(columns={'1': '9'})
source9_renamed = source9[['Baker', '1']].rename(columns={'1': '10'})

# The 'season' column is the same in all sources, so keep from source0 only.

# Now join all on 'Baker'
df = source0_renamed.merge(source1_renamed, on='Baker', how='inner') \
                    .merge(source2_renamed, on='Baker', how='inner') \
                    .merge(source3_renamed, on='Baker', how='inner') \
                    .merge(source4_renamed, on='Baker', how='inner') \
                    .merge(source5_renamed, on='Baker', how='inner') \
                    .merge(source6_renamed, on='Baker', how='inner') \
                    .merge(source7_renamed, on='Baker', how='inner') \
                    .merge(source8_renamed, on='Baker', how='inner') \
                    .merge(source9_renamed, on='Baker', how='inner')

# The target schema also has columns '2' through '7' as strings, which correspond to columns '2' through '7' in source0.
# So we need to add those columns from source0 to the final dataframe.

# Add columns '2' through '7' and 'season' from source0
df[['2', '3', '4', '5', '6', '7', 'season']] = source0[['2', '3', '4', '5', '6', '7', 'season']]

# The target schema has columns '8', '9', '10' as floats, but in source tables these columns are NaN or missing.
# The columns '8', '9', '10' in target are float and seem to correspond to the renamed columns from source7, source8, source9.
# We already renamed source7 '1' to '8', source8 '1' to '9', source9 '1' to '10'.
# But these columns are strings in source, so convert them to float, coercing errors to NaN.

for col in ['8', '9', '10']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Reorder columns to match target schema exactly
df = df[['Baker', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'season']]

# Write to CSV
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_44/target_multisource_mcts.csv', index=False)