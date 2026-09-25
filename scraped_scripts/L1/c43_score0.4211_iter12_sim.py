import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby(['facid', 'fac_type']).agg(
    capacity=('capacity', pd.Series.nunique),
    fac_name=('fac_name', pd.Series.nunique),
    fac_address=('fac_address', pd.Series.nunique),
    city_state_zip=('city_state_zip', pd.Series.nunique),
    owner=('owner', pd.Series.nunique),
    operator=('operator', pd.Series.nunique)
).reset_index()

agg['facid'] = agg['facid'].astype(int, errors='ignore')
agg['capacity'] = agg['capacity'].astype(int)
agg['fac_name'] = agg['fac_name'].astype(int)
agg['fac_address'] = agg['fac_address'].astype(int)
agg['city_state_zip'] = agg['city_state_zip'].astype(int)
agg['owner'] = agg['owner'].astype(int)
agg['operator'] = agg['operator'].astype(int)
agg['fac_type'] = agg['fac_type'].astype(str)

agg = agg[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)