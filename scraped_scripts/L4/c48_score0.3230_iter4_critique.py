import pandas as pd

# Read the single source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

# Define a helper to convert to int or pd.NA
def to_int_or_na(x):
    try:
        if pd.isna(x):
            return pd.NA
        return int(float(x))
    except:
        return pd.NA

# Group by the leftmost key columns of the target schema
grouped = df.groupby(['Initiator', 'WarNum', 'CcodeA', 'CcodeB'], dropna=False).agg({
    'StartMonth1': 'first',
    'StartDay1': 'first',
    'StartYear1': 'first',
    'EndMonth1': 'first',
    'EndDay1': 'first',
    'EndYear1': 'first',
    'Outcome': 'first',
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum'
}).reset_index()

# Construct the result DataFrame with exact target schema and names
result = pd.DataFrame()
result['Initiator'] = grouped['Initiator']

result['WarID'] = grouped['WarNum'].apply(to_int_or_na)
result['PolityID'] = grouped['CcodeA'].apply(to_int_or_na)
result['PolityName'] = grouped['CcodeB'].apply(to_int_or_na)

result['StartMonth'] = grouped['StartMonth1'].apply(to_int_or_na)
result['StartDay'] = grouped['StartDay1'].apply(to_int_or_na)
result['StartYear'] = grouped['StartYear1'].apply(to_int_or_na)

result['EndMonth'] = grouped['EndMonth1'].apply(to_int_or_na)
result['EndDay'] = grouped['EndDay1'].apply(to_int_or_na)
result['EndYear'] = grouped['EndYear1'].apply(to_int_or_na)

result['Outcome'] = grouped['Outcome'].apply(to_int_or_na)

side_a_deaths = grouped['SideADeaths'].fillna(0).apply(to_int_or_na).fillna(0)
side_b_deaths = grouped['SideBDeaths'].fillna(0).apply(to_int_or_na).fillna(0)
result['Deaths'] = side_a_deaths + side_b_deaths

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)