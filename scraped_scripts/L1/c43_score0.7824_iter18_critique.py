import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df['facid'] = pd.to_numeric(df['facid'], errors='coerce')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
df['fac_name'] = df['fac_name'].astype(str).str.len()
df['fac_address'] = df['fac_address'].astype(str).str.len()
df['city_state_zip'] = df['city_state_zip'].astype(str).str.len()
df['owner'] = df['owner'].astype(str).str.len()
df['operator'] = df['operator'].astype(str).str.len()

agg_df = df.groupby('fac_type').agg(
    facid=('facid', 'count'),
    capacity=('capacity', 'sum'),
    fac_name=('fac_name', 'sum'),
    fac_address=('fac_address', 'sum'),
    city_state_zip=('city_state_zip', 'sum'),
    owner=('owner', 'sum'),
    operator=('operator', 'sum')
).reset_index()

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)