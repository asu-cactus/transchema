import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

join_0_3 = pd.merge(s0, s3, on="zipcode", suffixes=('_x', '_y'))
join_1_2 = pd.merge(s1, s2, on="zipcode", suffixes=('_x_5', '_y_7'))

final = pd.merge(join_0_3, join_1_2, on="zipcode")

final = final.rename(columns={
    'businesses_x': 'businesses_x',
    'counts_x': 'counts_x',
    'businesses_y': 'businesses_y',
    'counts_y': 'counts_y',
    'businesses_x_5': 'businesses_x_5',
    'counts_x_6': 'counts_x_6',
    'businesses_y_7': 'businesses_y_7',
    'counts_y_8': 'counts_y_8'
})

# The columns from join_1_2 have suffixes _x_5 and _y_7, but counts columns are named 'counts' in source.
# So after merge, counts columns from s1 and s2 will be named 'counts_x_5' and 'counts_y_8' respectively.
# We need to rename them accordingly.

final = final.rename(columns={
    'counts_x_5': 'counts_x_6',
    'counts_y_7': 'businesses_y_7',
    'counts_y': 'counts_y_8'
})

# But the above renaming is inconsistent because 'counts_y' is already used from join_0_3.
# Let's carefully check the columns after merges:

# After join_0_3:
# columns: zipcode, businesses_x, counts_x, businesses_y, counts_y

# After join_1_2:
# columns: zipcode, businesses_x_5, counts_x_6, businesses_y_7, counts_y_8

# After final merge:
# columns: zipcode, businesses_x, counts_x, businesses_y, counts_y, businesses_x_5, counts_x_6, businesses_y_7, counts_y_8

# So no renaming needed except to ensure the suffixes are correct in the second merge.

# Let's fix the suffixes in second merge to get correct column names:

join_1_2 = pd.merge(s1, s2, on="zipcode", suffixes=('_x_5', '_y_7'))

# s1 columns: zipcode, businesses, counts
# s2 columns: zipcode, businesses, counts

# After merge:
# businesses_x_5 = businesses_x_5
# counts_x_5 = counts_x_5
# businesses_y_7 = businesses_y_7
# counts_y_7 = counts_y_7

# But suffixes only apply to overlapping columns except the join key.

# So columns after join_1_2:
# zipcode, businesses_x_5, counts_x_5, businesses_y_7, counts_y_7

# We want counts_x_6 and counts_y_8 in target, so rename counts_x_5 -> counts_x_6, counts_y_7 -> counts_y_8

join_1_2 = join_1_2.rename(columns={
    'counts_x_5': 'counts_x_6',
    'counts_y_7': 'counts_y_8'
})

final = pd.merge(join_0_3, join_1_2, on="zipcode")

final = final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
               'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv")