import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv", index_col=0)

joined = pd.merge(src0, src2, on="WarID", suffixes=('_0', '_2'))

# The join duplicates columns except WarID, so we need to unpivot the joined data to get one row per WarID and PolityName etc.
# We have columns like PolityName_0, PolityName_2, Outcome_0, Outcome_2, etc.
# We want to unpivot these pairs into rows, keeping WarID fixed.

# Identify columns to unpivot (all except WarID)
cols_0 = [c for c in joined.columns if c.endswith('_0')]
cols_2 = [c for c in joined.columns if c.endswith('_2')]

# Base columns: WarID
base = joined[['WarID']]

# Create two dataframes from the joined data, one for each suffix, then concat vertically
df_0 = joined[['WarID'] + cols_0].copy()
df_0.columns = ['WarID'] + [c[:-2] for c in cols_0]

df_2 = joined[['WarID'] + cols_2].copy()
df_2.columns = ['WarID'] + [c[:-2] for c in cols_2]

unpivoted = pd.concat([df_0, df_2], ignore_index=True)

# Now union with the other sources (src1, src3, src4) which have the same schema as src0 and src2
# Because the target schema matches source schemas, and the join+unpivot gave us two sources combined,
# we can union all sources together.

all_sources = pd.concat([unpivoted, src1, src3, src4], ignore_index=True)

# Convert columns to target schema and types
# Target schema: ['Outcome': int, 'WarID': int, 'PolityName': int, 'StartYear': int, 'StartMonth': int, 'StartDay': int, 'EndYear': int, 'EndMonth': int, 'EndDay': int, 'Initiator': int, 'Deaths': int]

# PolityName and Initiator are strings in sources, but target expects integers.
# We convert PolityName and Initiator to categorical codes (integers).
all_sources['PolityName'] = all_sources['PolityName'].astype('category').cat.codes
all_sources['Initiator'] = all_sources['Initiator'].astype('category').cat.codes

# For numeric columns, convert to numeric and then to Int64 (nullable integer) to preserve NaNs
int_cols = ['Outcome', 'WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Deaths']
for col in int_cols:
    all_sources[col] = pd.to_numeric(all_sources[col], errors='coerce').astype('Int64')

# Reorder columns to target schema order
all_sources = all_sources[['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']]

all_sources.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)