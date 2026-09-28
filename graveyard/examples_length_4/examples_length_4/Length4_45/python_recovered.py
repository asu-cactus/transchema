import pandas as pd
import numpy as np
import re

def extract_warshortname_int(s):
    # Try to get integer numeric part from string s
    # If s is numeric string, convert directly, else extract first integer
    if pd.isna(s):
        return 0
    if isinstance(s, int):
        return s
    if isinstance(s, float):
        return int(s)
    s = str(s)
    # try direct int cast
    try:
        return int(s)
    except:
        pass
    # find numbers in string
    m = re.search(r'\d+', s)
    if m:
        return int(m.group())
    else:
        return 0

# Paths of the source files
src0_path = 'autopipeline-benchmarks/github-pipelines/length4_45/test_0.csv'
src1_path = 'autopipeline-benchmarks/github-pipelines/length4_45/test_1.csv'
src2_path = 'autopipeline-benchmarks/github-pipelines/length4_45/test_2.csv'
src3_path = 'autopipeline-benchmarks/github-pipelines/length4_45/test_3.csv'

# Read source 0 and 1 with index_col=0 to ignore the first numerical index column
src0 = pd.read_csv(src0_path, index_col=0)
src1 = pd.read_csv(src1_path, index_col=0)
src2 = pd.read_csv(src2_path, index_col=0)
src3 = pd.read_csv(src3_path, index_col=0)

# Convert WarShortName columns to integers by extracting digits since target schema requires integer
src0['WarShortName'] = src0['WarShortName'].apply(extract_warshortname_int)
src1['WarShortName'] = src1['WarShortName'].apply(extract_warshortname_int)
src2['WarShortName'] = src2['WarShortName'].apply(extract_warshortname_int)
src3['WarShortName'] = src3['WarShortName'].apply(extract_warshortname_int)

# Union source 0 and 1 since they share the same schema ['WarID', 'WarShortName', 'WarType']
union_01 = pd.concat([src0, src1], axis=0, ignore_index=True)

# All joins will be on keys: ['WarID', 'WarShortName', 'WarType']
join_keys = ['WarID', 'WarShortName', 'WarType']

# Join union_01 with src2 (which includes IsIntervention)
df_merge = pd.merge(union_01, src2[join_keys + ['IsIntervention']], how='left', on=join_keys)

# Join the above result with src3 (which includes IsInternational)
df_merge = pd.merge(df_merge, src3[join_keys + ['IsInternational']], how='left', on=join_keys)

# Fill missing IsIntervention and IsInternational with 0 and convert to int
df_merge['IsInternational'] = df_merge['IsInternational'].fillna(0).astype(int)
df_merge['IsIntervention'] = df_merge['IsIntervention'].fillna(0).astype(int)

# Extract final columns in order and types:
# Target schema: ['WarType': int, 'WarID': int, 'WarShortName': int, 'IsInternational': int, 'IsIntervention': int]
df_result = df_merge[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']].copy()

df_result = df_result.astype({
    'WarType': int,
    'WarID': int,
    'WarShortName': int,
    'IsInternational': int,
    'IsIntervention': int,
})

# Write to target CSV path without index
target_path = 'autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_cot.csv'
df_result.to_csv(target_path, index=False)