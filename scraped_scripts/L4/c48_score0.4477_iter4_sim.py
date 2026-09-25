import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

agg_dict = {
    'WarNum': 'first',
    'CcodeA': 'first',
    'SideA': 'first',
    'CcodeB': 'first',
    'SideB': 'first',
    'StartMonth1': 'first',
    'StartDay1': 'first',
    'StartYear1': 'first',
    'EndMonth1': 'first',
    'EndDay1': 'first',
    'EndYear1': 'first',
    'Outcome': 'first',
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum'
}

grouped = df.groupby('Initiator', dropna=False).agg(agg_dict).reset_index()

def to_int_or_nan(x):
    try:
        if pd.isna(x):
            return pd.NA
        return int(float(x))
    except:
        return pd.NA

result = pd.DataFrame()
result['Initiator'] = grouped['Initiator']

result['WarID'] = grouped['WarNum'].apply(to_int_or_nan)
result['PolityID'] = grouped['CcodeA'].apply(to_int_or_nan)
result['PolityName'] = grouped['CcodeB'].apply(to_int_or_nan)

result['StartMonth'] = grouped['StartMonth1'].apply(to_int_or_nan)
result['StartDay'] = grouped['StartDay1'].apply(to_int_or_nan)
result['StartYear'] = grouped['StartYear1'].apply(to_int_or_nan)

result['EndMonth'] = grouped['EndMonth1'].apply(to_int_or_nan)
result['EndDay'] = grouped['EndDay1'].apply(to_int_or_nan)
result['EndYear'] = grouped['EndYear1'].apply(to_int_or_nan)

result['Outcome'] = grouped['Outcome'].apply(to_int_or_nan)

side_a_deaths = grouped['SideADeaths'].fillna(0).apply(to_int_or_nan).fillna(0)
side_b_deaths = grouped['SideBDeaths'].fillna(0).apply(to_int_or_nan).fillna(0)
result['Deaths'] = side_a_deaths + side_b_deaths

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)