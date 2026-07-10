import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

def pivot_source(df, suffix_business, suffix_count):
    pivoted = df.pivot(index='zipcode', columns='businesses', values='counts')
    pivoted = pivoted.reset_index()
    # Rename columns to match target pattern
    rename_map = {}
    for col in pivoted.columns:
        if col == 'zipcode':
            continue
        rename_map[col] = f"{suffix_business}_{col}"
    pivoted = pivoted.rename(columns=rename_map)
    return pivoted

p0 = pivot_source(df1, 'businesses_x', 'counts_x')  # Source1: Sidewalk Cafe
p0_counts = df1.pivot(index='zipcode', columns='businesses', values='counts').reset_index()
p0 = p0.copy()
# Actually, pivot_source only renames business columns, but counts columns are the same as business columns in pivot.
# The target schema has pairs of business name columns and counts columns, but source only has 'businesses' and 'counts'.
# So we need to create columns for business names and counts separately.

# Actually, the target schema has columns like:
# zipcode, businesses_x, counts_x, businesses_y, counts_y, businesses_x_5, counts_x_6, businesses_y_7, counts_y_8
# The pattern is that each source corresponds to two columns: one for business name, one for counts.
# But source tables only have 'businesses' and 'counts' columns.
# So the target table is a join of all sources on zipcode, with business names and counts from each source side by side.

# So we need to rename the 'businesses' column to the target business column name, and the 'counts' column to the target counts column name.
# But the source tables have multiple rows per zipcode, so we need to pivot them so that each zipcode has one row per source, with business and counts columns.

# Actually, the target schema shows that for each zipcode, there are multiple business/count pairs from different sources side by side.
# So the best approach is to pivot each source table so that each zipcode has multiple columns: one for business name, one for counts.
# But since each source has multiple rows per zipcode (multiple businesses), we need to aggregate or select the business/count pairs in some order.

# But the target examples show only one business/count pair per source per zipcode.
# So likely the target table is a join of the sources on zipcode, with the business and counts columns taken from the source tables as single values.

# But source tables have multiple rows per zipcode, so we need to aggregate or select one business/count pair per zipcode per source.

# The target examples show multiple business/count pairs per zipcode, but the columns are fixed:
# businesses_x, counts_x from source1 (Sidewalk Cafe)
# businesses_y, counts_y from source2 (Pawnbroker)
# businesses_x_5, counts_x_6 from source0 (Debt Collection Agency)
# businesses_y_7, counts_y_8 from source3 (Cigarette Retail Dealer)

# So the suffixes correspond to source tables:
# source1 -> businesses_x, counts_x
# source2 -> businesses_y, counts_y
# source0 -> businesses_x_5, counts_x_6
# source3 -> businesses_y_7, counts_y_8

# So we need to pick the business and counts from each source per zipcode, but each source has multiple businesses per zipcode.
# The target examples show only one business per source per zipcode, so likely the source tables have only one business per zipcode or we pick the first.

# But source tables have multiple businesses per zipcode, so we need to aggregate or pick the business with max counts or sum counts?

# The target examples show counts matching the counts in source tables for the business.

# So the best approach is to pivot each source table so that each zipcode has multiple columns, one per business, with counts as values.
# Then join all pivoted tables on zipcode.
# Then melt or stack the pivoted columns to get business/count pairs per source.
# But the target schema has fixed columns, so we must pick the business/count pair with max counts per source per zipcode.

# Alternatively, since the target schema has fixed columns, and the source tables have only one business type per source (e.g. source1 only Sidewalk Cafe),
# we can assume each source table contains only one business type, so we can take the business name as a constant per source.

# Let's check source examples:
# Source0: Debt Collection Agency only
# Source1: Sidewalk Cafe only
# Source2: Pawnbroker only
# Source3: Cigarette Retail Dealer only

# So each source table contains only one business type, but multiple zipcodes with counts.

# So for each source, we can aggregate counts per zipcode (sum counts), and add a column with the business name (constant per source).

# Then join all sources on zipcode.

# Rename columns to match target schema.

# Proceed accordingly.

def prepare_source(df, business_name, business_col, counts_col):
    agg = df.groupby('zipcode', as_index=False)['counts'].sum()
    agg[business_col] = business_name
    agg = agg.rename(columns={'counts': counts_col})
    return agg[['zipcode', business_col, counts_col]]

s0 = prepare_source(df0, 'Debt Collection Agency', 'businesses_x_5', 'counts_x_6')
s1 = prepare_source(df1, 'Sidewalk Cafe', 'businesses_x', 'counts_x')
s2 = prepare_source(df2, 'Pawnbroker', 'businesses_y', 'counts_y')
s3 = prepare_source(df3, 'Cigarette Retail Dealer', 'businesses_y_7', 'counts_y_8')

dfs = [s1, s2, s0, s3]

from functools import reduce
df_merged = reduce(lambda left, right: pd.merge(left, right, on='zipcode', how='outer'), dfs)

df_merged = df_merged.astype({
    'zipcode': 'Int64',
    'businesses_x': 'string',
    'counts_x': 'Int64',
    'businesses_y': 'string',
    'counts_y': 'Int64',
    'businesses_x_5': 'string',
    'counts_x_6': 'Int64',
    'businesses_y_7': 'string',
    'counts_y_8': 'Int64'
})

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)