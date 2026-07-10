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

j0 = pd.merge(s4, s0, on="zipcode", how="outer")
j1 = pd.merge(j0, s1, on="zipcode", how="outer", suffixes=('_x', '_y'))
j2 = pd.merge(j1, s3, on="zipcode", how="outer", suffixes=('_x', '_y'))
j3 = pd.merge(j2, s7, on="zipcode", how="outer", suffixes=('_x', '_y'))
j4 = pd.merge(j3, s2, on="zipcode", how="outer")
j5 = pd.merge(j4, s5, on="zipcode", how="outer")
j6 = pd.merge(j5, s6, on="zipcode", how="outer", suffixes=('_x_10', '_y_11'))
j7 = pd.merge(j6, s8, on="zipcode", how="outer", suffixes=('_x_10', '_y_11'))
j8 = pd.merge(j7, s9, on="zipcode", how="outer", suffixes=('_x_6', '_y_8'))

# Rename columns to match target schema exactly
# From s1 and s3 and s7 and s9, businesses and counts columns appear multiple times, rename accordingly:
# s1: businesses, counts -> businesses_x, counts_x
# s3: businesses, counts -> businesses_x_5, counts_x_6
# s7: businesses, counts -> businesses_y_7, counts_y_8
# s9: businesses, counts -> businesses_y, counts_y

# After merges, columns from s1 and s3 and s7 and s9 have suffixes, fix them:
# j1 merge added suffixes _x and _y for s1 columns (businesses, counts)
# j2 merge added suffixes _x and _y for s3 columns (businesses, counts)
# j3 merge added suffixes _x and _y for s7 columns (businesses, counts)
# j8 merge added suffixes _x_6 and _y_8 for s9 columns (businesses, counts)

# Rename accordingly:
j8 = j8.rename(columns={
    'businesses_x': 'businesses_x',
    'counts_x': 'counts_x',
    'businesses_x_x': 'businesses_x_5',
    'counts_x_y': 'counts_x_6',
    'businesses_y_x': 'businesses_y_7',
    'counts_y_y': 'counts_y_8',
    'businesses_y': 'businesses_y',
    'counts_y': 'counts_y',
    'boro': 'boro',
    'total_crime': 'total_crime',
    'violation': 'violation',
    'misdemeanor': 'misdemeanor',
    'felony': 'felony',
    'theft': 'theft',
    'assault': 'assault',
    'harassment': 'harassment',
    'indicator': 'indicator',
    'counts_x_10': 'counts_x_10',
    'counts_y_11': 'counts_y_11',
    'counts_x_6': 'counts_x_6',
    'counts_y_8': 'counts_y_8',
    'counts_x_10': 'counts_x_10',
    'counts_y_11': 'counts_y_11',
    'counts': 'counts'
})

# Because suffixes may have caused some columns to be duplicated or renamed differently, fix columns carefully:
# Let's explicitly rename columns from each source after merges:

# After all merges, columns are:
# zipcode
# boro (from s4)
# total_crime, violation, misdemeanor, felony (from s0)
# businesses_x, counts_x (from s1)
# businesses_x_5, counts_x_6 (from s3)
# businesses_y_7, counts_y_8 (from s7)
# indicator, counts (from s2)
# theft, assault, harassment (from s5)
# counts_x_10 (from s6)
# counts_y_11 (from s8)
# businesses_y, counts_y (from s9)

# The suffixes in merges caused some columns to be named with suffixes, so let's rename explicitly:

j8 = j8.rename(columns={
    'businesses_x': 'businesses_x',
    'counts_x': 'counts_x',
    'businesses_x_x': 'businesses_x_5',
    'counts_x_y': 'counts_x_6',
    'businesses_y_x': 'businesses_y_7',
    'counts_y_y': 'counts_y_8',
    'businesses_y': 'businesses_y',
    'counts_y': 'counts_y',
    'counts_x_10': 'counts_x_10',
    'counts_y_11': 'counts_y_11'
})

# Select and reorder columns to match target schema exactly:
final_cols = ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
              'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
              'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
              'total_crime', 'violation', 'misdemeanor', 'felony',
              'theft', 'assault', 'harassment']

result = j8[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")