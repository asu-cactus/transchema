import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

def pivot_businesses(df, prefix):
    p = df.pivot(index='zipcode', columns='businesses', values='counts')
    p.columns = [f"{prefix}{i}" for i in range(len(p.columns)*2)]
    # We want to create pairs of columns: businesses_x, counts_x, businesses_y, counts_y, etc.
    # But pivot gives counts only, so we need to reconstruct businesses names as columns.
    # Instead, we do a pivot that returns a DataFrame with multiindex columns (businesses, counts)
    # Since we only have counts, we must reconstruct the businesses columns by sorting businesses and assigning them to columns.
    # Instead, do a pivot with businesses as columns and counts as values, then flatten.
    # But target schema expects columns like businesses_x, counts_x, businesses_y, counts_y, etc.
    # So we must create columns for businesses names and counts interleaved.
    # We'll do this by sorting businesses alphabetically and assigning them to columns in order.

    # Actually, better to do this outside this function.

    return p

# Combine all business-count sources with pivot, then assign columns accordingly
# Sources with businesses and counts: s1, s3, s7, s9
# We will pivot each, then join on zipcode, then flatten columns to match target schema.

p1 = s1.pivot(index='zipcode', columns='businesses', values='counts')
p3 = s3.pivot(index='zipcode', columns='businesses', values='counts')
p7 = s7.pivot(index='zipcode', columns='businesses', values='counts')
p9 = s9.pivot(index='zipcode', columns='businesses', values='counts')

# Rename columns to avoid collision before join
p1.columns = [f"x_{c}" for c in p1.columns]
p3.columns = [f"x5_{c}" for c in p3.columns]
p7.columns = [f"y7_{c}" for c in p7.columns]
p9.columns = [f"x_{c}" for c in p9.columns]

# Join all pivoted business counts on zipcode
businesses = p1.join(p3, how='outer').join(p7, how='outer').join(p9, how='outer')

# Now we want to create columns in the target schema order:
# ['businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8']
# The target examples show 4 pairs of business/count columns:
# businesses_x, counts_x from s9 (Sidewalk Cafe)
# businesses_y, counts_y from s1 (Pawnbroker)
# businesses_x_5, counts_x_6 from s3 (Debt Collection Agency)
# businesses_y_7, counts_y_8 from s7 (Cigarette Retail Dealer)

# From the example, the order is:
# s9 (Sidewalk Cafe) -> businesses_x, counts_x
# s1 (Pawnbroker) -> businesses_y, counts_y
# s3 (Debt Collection Agency) -> businesses_x_5, counts_x_6
# s7 (Cigarette Retail Dealer) -> businesses_y_7, counts_y_8

# So we must extract the single business name and counts from each pivoted df, because each source has only one business type per source.

# Extract business names from each source (unique businesses per source)
b_s9 = s9['businesses'].unique()
b_s1 = s1['businesses'].unique()
b_s3 = s3['businesses'].unique()
b_s7 = s7['businesses'].unique()

# Each source has only one business type:
# s9: Sidewalk Cafe
# s1: Pawnbroker
# s3: Debt Collection Agency
# s7: Cigarette Retail Dealer

# So create columns accordingly:

df = pd.DataFrame(index=businesses.index)

# businesses_x and counts_x from s9
df['businesses_x'] = b_s9[0]
df['counts_x'] = businesses.get(f"x_{b_s9[0]}", pd.Series(index=businesses.index))

# businesses_y and counts_y from s1
df['businesses_y'] = b_s1[0]
df['counts_y'] = businesses.get(f"x_{b_s1[0]}", pd.Series(index=businesses.index))

# businesses_x_5 and counts_x_6 from s3
df['businesses_x_5'] = b_s3[0]
df['counts_x_6'] = businesses.get(f"x5_{b_s3[0]}", pd.Series(index=businesses.index))

# businesses_y_7 and counts_y_8 from s7
df['businesses_y_7'] = b_s7[0]
df['counts_y_8'] = businesses.get(f"y7_{b_s7[0]}", pd.Series(index=businesses.index))

df.index.name = 'zipcode'
df.reset_index(inplace=True)

# Join with s0 (zipcode, total_crime, violation, misdemeanor, felony)
df = df.merge(s0, on='zipcode', how='left')

# Join with s2 (zipcode, indicator, counts)
df = df.merge(s2, on='zipcode', how='left')

# Join with s4 (boro, zipcode)
df = df.merge(s4, on='zipcode', how='left')

# Join with s5 (zipcode, theft, assault, harassment)
df = df.merge(s5, on='zipcode', how='left')

# Join with s6 (zipcode, counts) - this is counts_x_10 in target
df = df.merge(s6.rename(columns={'counts':'counts_x_10'}), on='zipcode', how='left')

# Join with s8 (zipcode, counts) - this is counts_y_11 in target
df = df.merge(s8.rename(columns={'counts':'counts_y_11'}), on='zipcode', how='left')

# Reorder columns to match target schema exactly
cols = ['zipcode',
        'businesses_x', 'counts_x',
        'businesses_y', 'counts_y',
        'businesses_x_5', 'counts_x_6',
        'businesses_y_7', 'counts_y_8',
        'boro',
        'counts_x_10', 'counts_y_11',
        'indicator', 'counts',
        'total_crime', 'violation', 'misdemeanor', 'felony',
        'theft', 'assault', 'harassment']

df = df[cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)