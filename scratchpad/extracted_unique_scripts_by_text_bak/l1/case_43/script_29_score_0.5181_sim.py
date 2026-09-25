import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby(['facid', 'fac_type']).agg(
    capacity_sum=pd.NamedAgg(column='capacity', aggfunc='sum'),
    fac_name_count=pd.NamedAgg(column='fac_name', aggfunc='count'),
    fac_address_count=pd.NamedAgg(column='fac_address', aggfunc='count'),
    city_state_zip_count=pd.NamedAgg(column='city_state_zip', aggfunc='count'),
    owner_count=pd.NamedAgg(column='owner', aggfunc='count'),
    operator_count=pd.NamedAgg(column='operator', aggfunc='count')
).reset_index()

agg = agg.rename(columns={
    'facid': 'facid',
    'fac_type': 'fac_type',
    'capacity_sum': 'capacity',
    'fac_name_count': 'fac_name',
    'fac_address_count': 'fac_address',
    'city_state_zip_count': 'city_state_zip',
    'owner_count': 'owner',
    'operator_count': 'operator'
})

agg['facid'] = agg['facid'].astype(int, errors='ignore')
agg['capacity'] = agg['capacity'].astype(int, errors='ignore')
agg['fac_name'] = agg['fac_name'].astype(int)
agg['fac_address'] = agg['fac_address'].astype(int)
agg['city_state_zip'] = agg['city_state_zip'].astype(int)
agg['owner'] = agg['owner'].astype(int)
agg['operator'] = agg['operator'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)