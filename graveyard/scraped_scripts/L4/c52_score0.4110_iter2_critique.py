import pandas as pd

# Read all sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_52/training_3.csv", index_col=0)

# Add missing PolityName column to src3 (which lacks it) with NaN
if 'PolityName' not in src3.columns:
    src3['PolityName'] = pd.NA

# Concatenate all sources (union)
all_sources = pd.concat([src0, src1, src2, src3], ignore_index=True, sort=False)

# Convert PolityName to categorical codes (integer) to match target schema
# Use factorize to assign integer codes, missing values get -1, convert to 0 for missing
codes, uniques = pd.factorize(all_sources['PolityName'])
all_sources['PolityName'] = codes
all_sources['PolityName'] = all_sources['PolityName'].replace(-1, 0).astype(int)

# Convert Side to integer if not already
all_sources['Side'] = pd.to_numeric(all_sources['Side'], errors='coerce').fillna(0).astype(int)

# Define group by columns (leftmost columns of target schema that are int and unique)
group_by_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay']

# Convert group by columns to numeric (int), fill NaN with 0
for col in group_by_cols:
    all_sources[col] = pd.to_numeric(all_sources[col], errors='coerce').fillna(0).astype(int)

# For aggregation columns, convert to numeric as well
agg_cols = ['EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths']
for col in agg_cols:
    all_sources[col] = pd.to_numeric(all_sources[col], errors='coerce')

# Aggregate:
# For EndYear, EndMonth, EndDay, Side, Outcome: take max (assuming latest or dominant)
# For Deaths: sum
# For PolityName: take first (already integer codes)
agg_dict = {
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Side': 'max',
    'Outcome': 'max',
    'Deaths': 'sum',
    'PolityName': 'first'
}

result = all_sources.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure all columns are integer type as per target schema
int_cols = ['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']

for c in int_cols:
    if c in result.columns:
        # For Deaths, sum may produce float, convert to int safely by rounding
        if c == 'Deaths':
            result[c] = result[c].fillna(0).round().astype(int)
        else:
            result[c] = result[c].fillna(0).astype(int)

# Reorder columns to match target schema exactly
result = result[['IsInitiator', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
                 'EndYear', 'EndMonth', 'EndDay', 'Side', 'Outcome', 'Deaths', 'PolityName']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_52/target_multisource_mcts.csv", index=False)