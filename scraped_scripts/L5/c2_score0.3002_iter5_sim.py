import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_2/training_5.csv", index_col=0)

pivot_4 = df4.pivot(index='zipcode', columns='businesses', values='counts').reset_index()
pivot_4.columns.name = None
pivot_4 = pivot_4.rename(columns={
    'Sidewalk Cafe': 'businesses_x',
    'counts': 'counts_x'
})
pivot_4 = pivot_4.rename(columns=lambda x: x if x == 'zipcode' or x == 'businesses_x' else f"counts_x" if x == 'Sidewalk Cafe' else x)
# Actually, pivot creates columns named after businesses, values are counts, so rename columns accordingly:
pivot_4 = df4.pivot(index='zipcode', columns='businesses', values='counts').reset_index()
pivot_4.columns.name = None
pivot_4 = pivot_4.rename(columns={
    'Sidewalk Cafe': 'counts_x'
})
pivot_4 = pivot_4.rename(columns={'zipcode':'zipcode'})
pivot_4 = pivot_4.rename(columns={'Sidewalk Cafe':'counts_x'})
# But we need businesses_x as string columns, counts_x as integer columns.
# The target schema has businesses_x as string, counts_x as integer.
# The source df4 has businesses and counts columns.
# The pivot creates columns named after businesses with counts as values.
# But the target schema expects businesses_x as string (business name), counts_x as integer (count).
# So we need to create two columns: businesses_x (string) and counts_x (integer).
# The pivot creates counts per business as columns, but we want only one business per column.
# The target examples show businesses_x = 'Sidewalk Cafe', counts_x = count of Sidewalk Cafe.
# So we can create businesses_x column with constant 'Sidewalk Cafe' and counts_x from pivoted counts.

pivot_4 = df4.groupby('zipcode').agg({'counts': 'sum'}).reset_index()
# This is not correct, we want counts per business Sidewalk Cafe per zipcode.
# So better to filter df4 for Sidewalk Cafe and rename columns.

sidewalk = df4[df4['businesses'] == 'Sidewalk Cafe'][['zipcode', 'counts']].rename(columns={'counts':'counts_x'})
sidewalk['businesses_x'] = 'Sidewalk Cafe'

pivot_2 = df2[df2['businesses'] == 'Pawnbroker'][['zipcode', 'counts']].rename(columns={'counts':'counts_y'})
pivot_2['businesses_y'] = 'Pawnbroker'

pivot_0 = df0[df0['businesses'] == 'Debt Collection Agency'][['zipcode', 'counts']].rename(columns={'counts':'counts_x_6'})
pivot_0['businesses_x_5'] = 'Debt Collection Agency'

pivot_3 = df3[df3['businesses'] == 'Cigarette Retail Dealer'][['zipcode', 'counts']].rename(columns={'counts':'counts_y_8'})
pivot_3['businesses_y_7'] = 'Cigarette Retail Dealer'

join_1 = pd.merge(sidewalk, pivot_2, on='zipcode', how='outer')
join_2 = pd.merge(join_1, pivot_0, on='zipcode', how='outer')
join_3 = pd.merge(join_2, df1, on='zipcode', how='outer')
join_4 = pd.merge(join_3, pivot_3, on='zipcode', how='outer')

df5_renamed = df5.rename(columns={'businesses': 'businesses'})

final = pd.merge(join_4, df5_renamed, on='zipcode', how='outer')

final = final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8', 'boro', 'businesses']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_2/target_multisource_mcts.csv", index=False)