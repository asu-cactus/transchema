import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby('fac_type', dropna=False).agg(
    facid=pd.NamedAgg(column='facid', aggfunc='count'),
    capacity=pd.NamedAgg(column='capacity', aggfunc='sum'),
    fac_name=pd.NamedAgg(column='fac_name', aggfunc='count'),
    fac_address=pd.NamedAgg(column='fac_address', aggfunc='count'),
    city_state_zip=pd.NamedAgg(column='city_state_zip', aggfunc='count'),
    owner=pd.NamedAgg(column='owner', aggfunc='count'),
    operator=pd.NamedAgg(column='operator', aggfunc='count'),
).reset_index()

# Convert all columns to int where appropriate
agg['facid'] = agg['facid'].astype(int)
agg['capacity'] = agg['capacity'].astype(int)
agg['fac_name'] = agg['fac_name'].astype(int)
agg['fac_address'] = agg['fac_address'].astype(int)
agg['city_state_zip'] = agg['city_state_zip'].astype(int)
agg['owner'] = agg['owner'].astype(int)
agg['operator'] = agg['operator'].astype(int)

agg = agg[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)