import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

agg = df0.groupby(['Artist', 'Years Waited', '# of Years Nominated']).agg(
    Year_Inducted_min=('Year Inducted', 'min'),
    Year_Inducted_max=('Year Inducted', 'max'),
    Inducted_By_count=('Inducted By', 'count')
).reset_index()

# From the aggregation, choose Year Inducted as the min (or max) - target examples show float, so pick min
agg['Year Inducted'] = agg['Year_Inducted_min']

# We do not need Year_Inducted_max and Inducted_By_count for final output, drop them
agg = agg.drop(columns=['Year_Inducted_min', 'Year_Inducted_max', 'Inducted_By_count'])

# Join with df1 on Artist to get Influenced
joined_1 = pd.merge(agg, df1, on='Artist', how='left')

# Join with df3 on Artist to get Certified Units (Millions)
joined_2 = pd.merge(joined_1, df3, on='Artist', how='left')

# The target schema is:
# ['Artist': string, 'Year Inducted': float, 'Years Waited': integer, '# of Years Nominated': integer, 'Inducted By': string, 'Influenced': integer, 'Certified Units (Millions)': float]
# We do not have 'Inducted By' in the aggregation result because it was aggregated by count.
# The source 0 has 'Inducted By' column, but it was aggregated by count in the first step.
# The target examples show 'Inducted By' as string, e.g. "Melissa Etheridge".
# So we need to get 'Inducted By' string values for each Artist.
# Since source0 has multiple rows per Artist, we can take the most frequent 'Inducted By' per Artist from source0.

inducted_by_mode = df0.groupby('Artist')['Inducted By'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA).reset_index()

final = pd.merge(joined_2, inducted_by_mode, on='Artist', how='left')

# Fix data types to match target schema
final['Year Inducted'] = final['Year Inducted'].astype(float)
final['Years Waited'] = pd.to_numeric(final['Years Waited'], errors='coerce').astype('Int64')
final['# of Years Nominated'] = pd.to_numeric(final['# of Years Nominated'], errors='coerce').astype('Int64')
final['Influenced'] = pd.to_numeric(final['Influenced'], errors='coerce').astype('Int64')
final['Certified Units (Millions)'] = pd.to_numeric(final['Certified Units (Millions)'], errors='coerce').astype(float)
final['Inducted By'] = final['Inducted By'].astype('string')

final = final[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)