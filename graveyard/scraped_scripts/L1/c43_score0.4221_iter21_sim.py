import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

group_cols = ['facid', 'fac_type', 'capacity', 'fac_name', 'fac_address', 'city_state_zip']

agg_df = df.groupby(group_cols).agg(
    owner=('owner', pd.Series.nunique),
    operator=('operator', pd.Series.nunique)
).reset_index()

agg_df['fac_type'] = agg_df['fac_type'].astype(str)
agg_df['facid'] = agg_df['facid'].astype(str)
agg_df['capacity'] = pd.to_numeric(agg_df['capacity'], errors='coerce').fillna(0).astype(int)
agg_df['fac_name'] = agg_df['fac_name'].astype(str)
agg_df['fac_address'] = agg_df['fac_address'].astype(str)
agg_df['city_state_zip'] = agg_df['city_state_zip'].astype(str)
agg_df['owner'] = agg_df['owner'].astype(int)
agg_df['operator'] = agg_df['operator'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)