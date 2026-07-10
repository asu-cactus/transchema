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

def unpivot_businesses(df, suffix):
    df_ = df.rename(columns={'businesses':'businesses_'+suffix, 'counts':'counts_'+suffix})
    return df_

u1 = unpivot_businesses(s1, 'x')
u3 = unpivot_businesses(s3, 'x_5')
u7 = unpivot_businesses(s7, 'y_7')
u9 = unpivot_businesses(s9, 'x_5')  # but target has businesses_x_5 and businesses_y_7, so we must assign carefully

# We have 4 source tables with schema (zipcode, businesses, counts):
# s1 -> businesses_x, counts_x
# s3 -> businesses_x_5, counts_x_6
# s7 -> businesses_y_7, counts_y_8
# s9 -> businesses_x (again?), counts_x (again?)

# From target examples, businesses_x_5 and counts_x_6 come from s3
# businesses_y_7 and counts_y_8 come from s7
# businesses_x and counts_x come from s9 (Sidewalk Cafe) and s1 (Pawnbroker)
# But s1 and s9 both have businesses_x and counts_x? The target has businesses_x and counts_x, and also businesses_x_5 and counts_x_6, and businesses_y and counts_y, and businesses_y_7 and counts_y_8.

# The target columns:
# zipcode
# businesses_x, counts_x
# businesses_y, counts_y
# businesses_x_5, counts_x_6
# businesses_y_7, counts_y_8
# boro
# counts_x_10, counts_y_11
# indicator, counts
# total_crime, violation, misdemeanor, felony
# theft, assault, harassment

# We see counts_x_10 and counts_y_11 in target, which are not from the above 4 sources with businesses.

# s1: businesses_x, counts_x (Pawnbroker)
# s9: businesses_x, counts_x (Sidewalk Cafe)
# s3: businesses_x_5, counts_x_6 (Debt Collection Agency)
# s7: businesses_y_7, counts_y_8 (Cigarette Retail Dealer)

# But target also has businesses_y and counts_y (Pawnbroker in example), so s1 is businesses_y or businesses_x? The example shows businesses_x=Sidewalk Cafe, businesses_y=Pawnbroker, so s9 is businesses_x, s1 is businesses_y.

# So we must rename s9 as businesses_x, s1 as businesses_y.

u1 = s1.rename(columns={'businesses':'businesses_y', 'counts':'counts_y'})
u3 = s3.rename(columns={'businesses':'businesses_x_5', 'counts':'counts_x_6'})
u7 = s7.rename(columns={'businesses':'businesses_y_7', 'counts':'counts_y_8'})
u9 = s9.rename(columns={'businesses':'businesses_x', 'counts':'counts_x'})

# Now join these 4 on zipcode with outer join to get all businesses columns in one df
df_biz = pd.merge(u9, u1, on='zipcode', how='outer')
df_biz = pd.merge(df_biz, u3, on='zipcode', how='outer')
df_biz = pd.merge(df_biz, u7, on='zipcode', how='outer')

# counts_x_10 and counts_y_11 come from where? Looking at source schemas:
# s6: ['zipcode', 'counts'] (108 tuples)
# s8: ['zipcode', 'counts'] (180 tuples)
# They likely correspond to counts_x_10 and counts_y_11 respectively.

s6_renamed = s6.rename(columns={'counts':'counts_x_10'})
s8_renamed = s8.rename(columns={'counts':'counts_y_11'})

df_biz = pd.merge(df_biz, s6_renamed, on='zipcode', how='outer')
df_biz = pd.merge(df_biz, s8_renamed, on='zipcode', how='outer')

# Join boro from s4
df_biz = pd.merge(df_biz, s4, on='zipcode', how='left')

# Join s0 (total_crime, violation, misdemeanor, felony)
df_biz = pd.merge(df_biz, s0, on='zipcode', how='left')

# Join s5 (theft, assault, harassment)
df_biz = pd.merge(df_biz, s5, on='zipcode', how='left')

# Join s2 (indicator, counts)
df_biz = pd.merge(df_biz, s2, on='zipcode', how='left')

# Join s6 and s8 already joined as counts_x_10 and counts_y_11

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

df_biz = df_biz[cols]

df_biz.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")