import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

# Join Source5_4_0 and Source5_4_2 on 'Artist' using inner join
joined_0_2 = pd.merge(df0, df2, on="Artist", how="inner", suffixes=('_0', '_2'))

# After join, columns from df0 and df2 overlap except 'Inducted By' only in df0
# We need to coalesce columns from df0 and df2 for 'Year Inducted', 'Years Waited', '# of Years Nominated'
# Because df2 has NaNs in 'Year Inducted' etc., prefer df0's values, else df2's

def coalesce(col0, col2):
    return col0.combine_first(col2)

joined_0_2['Year Inducted'] = coalesce(joined_0_2['Year Inducted_0'], joined_0_2['Year Inducted_2'])
joined_0_2['Years Waited'] = coalesce(joined_0_2['Years Waited_0'], joined_0_2['Years Waited_2'])
joined_0_2['# of Years Nominated'] = coalesce(joined_0_2['# of Years Nominated_0'], joined_0_2['# of Years Nominated_2'])

# Keep 'Inducted By' from df0
joined_0_2 = joined_0_2.drop(columns=['Year Inducted_0', 'Year Inducted_2', 'Years Waited_0', 'Years Waited_2', '# of Years Nominated_0', '# of Years Nominated_2'])

# Join with Source5_4_1 on 'Artist' using inner join
joined_0_2_1 = pd.merge(joined_0_2, df1, on="Artist", how="inner")

# Join with Source5_4_3 on 'Artist' using inner join
final_df = pd.merge(joined_0_2_1, df3, on="Artist", how="inner")

# Convert columns to correct types
final_df['Year Inducted'] = pd.to_numeric(final_df['Year Inducted'], errors='coerce')
final_df['Years Waited'] = pd.to_numeric(final_df['Years Waited'], errors='coerce').astype('Int64')
final_df['# of Years Nominated'] = pd.to_numeric(final_df['# of Years Nominated'], errors='coerce').astype('Int64')
final_df['Influenced'] = pd.to_numeric(final_df['Influenced'], errors='coerce').astype('Int64')
final_df['Certified Units (Millions)'] = pd.to_numeric(final_df['Certified Units (Millions)'], errors='coerce')

# Group by 'Artist' and aggregate by first() to remove duplicates if any
agg_dict = {
    'Year Inducted': 'first',
    'Years Waited': 'first',
    '# of Years Nominated': 'first',
    'Inducted By': 'first',
    'Influenced': 'first',
    'Certified Units (Millions)': 'first'
}

final_df = final_df.groupby('Artist', as_index=False).agg(agg_dict)

# Reorder columns to match target schema
final_df = final_df[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)