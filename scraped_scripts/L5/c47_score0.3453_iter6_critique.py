import pandas as pd

# Read all source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_47/training_4.csv", index_col=0)

# Concatenate all sources (UNION)
all_sources = pd.concat([src0, src1, src2, src3, src4], ignore_index=True)

# Convert PolityName and Initiator to categorical codes (integers)
all_sources['PolityName'] = all_sources['PolityName'].astype('category').cat.codes
all_sources['Initiator'] = all_sources['Initiator'].astype('category').cat.codes

# Convert numeric columns to numeric types with nullable integer dtype
int_cols = ['Outcome', 'WarID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Deaths']
for col in int_cols:
    all_sources[col] = pd.to_numeric(all_sources[col], errors='coerce').astype('Int64')

# Group by Outcome and WarID, aggregate as specified
agg_dict = {
    'PolityName': 'max',
    'StartYear': 'max',
    'StartMonth': 'max',
    'StartDay': 'max',
    'EndYear': 'max',
    'EndMonth': 'max',
    'EndDay': 'max',
    'Initiator': 'max',
    'Deaths': 'sum'
}

grouped = all_sources.groupby(['Outcome', 'WarID'], dropna=False).agg(agg_dict).reset_index()

# Reorder columns to target schema order
final_df = grouped[['Outcome', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay',
                    'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Deaths']]

# Write to output CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_47/target_multisource_mcts.csv", index=False)