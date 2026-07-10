import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type and count distinct for all other columns
pivoted = df0.groupby('fac_type').agg({
    'facid': pd.Series.nunique,
    'capacity': pd.Series.nunique,
    'fac_name': pd.Series.nunique,
    'fac_address': pd.Series.nunique,
    'city_state_zip': pd.Series.nunique,
    'owner': pd.Series.nunique,
    'operator': pd.Series.nunique
}).reset_index()

# Ensure types match target schema: fac_type string, others int
pivoted = pivoted.astype({
    'fac_type': str,
    'facid': int,
    'capacity': int,
    'fac_name': int,
    'fac_address': int,
    'city_state_zip': int,
    'owner': int,
    'operator': int
})

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)