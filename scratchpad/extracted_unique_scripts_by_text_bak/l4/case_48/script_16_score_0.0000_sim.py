import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

group_cols = [
    'Initiator', 'WarNum', 'CcodeA', 'CcodeB', 
    'StartMonth1', 'StartDay1', 'StartYear1', 
    'EndMonth1', 'EndDay1', 'EndYear1', 'Outcome'
]

agg_df = df0.groupby(group_cols, dropna=False, as_index=False).agg({
    'SideADeaths': 'sum',
    'SideBDeaths': 'sum'
})

agg_df['Deaths'] = agg_df['SideADeaths'].fillna(0) + agg_df['SideBDeaths'].fillna(0)

result = pd.DataFrame({
    'Initiator': agg_df['Initiator'].astype(str),
    'WarID': pd.to_numeric(agg_df['WarNum'], errors='coerce').astype('Int64'),
    'PolityID': pd.to_numeric(agg_df['CcodeA'], errors='coerce').astype('Int64'),
    'PolityName': pd.to_numeric(agg_df['CcodeB'], errors='coerce').astype('Int64'),
    'StartMonth': pd.to_numeric(agg_df['StartMonth1'], errors='coerce').astype('Int64'),
    'StartDay': pd.to_numeric(agg_df['StartDay1'], errors='coerce').astype('Int64'),
    'StartYear': pd.to_numeric(agg_df['StartYear1'], errors='coerce').astype('Int64'),
    'EndMonth': pd.to_numeric(agg_df['EndMonth1'], errors='coerce').astype('Int64'),
    'EndDay': pd.to_numeric(agg_df['EndDay1'], errors='coerce').astype('Int64'),
    'EndYear': pd.to_numeric(agg_df['EndYear1'], errors='coerce').astype('Int64'),
    'Outcome': pd.to_numeric(agg_df['Outcome'], errors='coerce').astype('Int64'),
    'Deaths': agg_df['Deaths'].astype('Int64')
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)