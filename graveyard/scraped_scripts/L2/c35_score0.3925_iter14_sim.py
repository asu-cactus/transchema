import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_35/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_35/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_35/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# UNPIVOT Source2_35_1: The partial plan says UNPIVOT on Source2_35_1
# Source2_35_1 has columns including 'Date' and 'NumMosquitos' (target needs Date, ResultDir, NumMosquitos)
# The hint says UNPIVOT and UNION with Source2_35_1, but Source2_35_0 has ResultDir, Source2_35_1 has NumMosquitos.
# So we unpivot Source2_35_1 to get Date and NumMosquitos (already have Date and NumMosquitos)
# Actually, Source2_35_1 already has Date and NumMosquitos columns, no unpivot needed on it.
# But the partial plan says UNPIVOT on Source2_35_1, so let's check if unpivot is needed:
# Source2_35_1 schema: ['Date', 'Address', 'Species', 'Block', 'Street', 'Trap', 'AddressNumberAndStreet', 'Latitude', 'Longitude', 'AddressAccuracy', 'NumMosquitos', 'WnvPresent']
# Target schema: ['Date', 'ResultDir', 'NumMosquitos']
# ResultDir is only in Source2_35_0.
# So we need to join Source2_35_1 and Source2_35_0 on Date to get ResultDir and NumMosquitos together.
# The partial plan says UNPIVOT on Source2_35_1, but no columns to unpivot for target.
# Possibly the partial plan is a hint to unpivot Source2_35_1 if it had multiple mosquito counts per species or trap.
# But since target only needs NumMosquitos (already a column), no unpivot needed.
# So we skip unpivot and just join on Date.

# Join on Date to get ResultDir and NumMosquitos together
df_joined = pd.merge(df0[['Date', 'ResultDir']], df1[['Date', 'NumMosquitos']], on='Date', how='inner')

# Convert types to match target schema
df_joined['Date'] = df_joined['Date'].astype(str)
df_joined['ResultDir'] = pd.to_numeric(df_joined['ResultDir'], errors='coerce')
df_joined['NumMosquitos'] = pd.to_numeric(df_joined['NumMosquitos'], errors='coerce')

df_joined = df_joined[['Date', 'ResultDir', 'NumMosquitos']]

df_joined.to_csv(target_path, index=False)