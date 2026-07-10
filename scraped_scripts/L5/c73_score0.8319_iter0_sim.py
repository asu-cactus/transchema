import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_5.csv", index_col=0)

# GROUP_BY Area_name on df0 (no aggregation needed for join, but we keep it as is)
# The partial plan suggests grouping by Area_name, but since no aggregation is specified,
# we just keep df0 as is (no duplicates expected on Area_name for join keys).

# Join df0 and df1 on fips_code
join_0 = pd.merge(df0, df1, on="fips_code", how="inner", suffixes=('_x', '_y'))

# Join with df2 on fips_code
join_1 = pd.merge(join_0, df2, on="fips_code", how="inner", suffixes=('', '_2'))

# Join with df3 on fips_code
join_2 = pd.merge(join_1, df3, on="fips_code", how="inner", suffixes=('', '_3'))

# Join with df4 on fips_code
join_3 = pd.merge(join_2, df4, on="fips_code", how="inner", suffixes=('', '_4'))

# Join with df5 on fips_code
join_4 = pd.merge(join_3, df5, on="fips_code", how="inner", suffixes=('', '_5'))

# Rename columns to match target schema exactly
# Target columns:
# ['state_x': string, 'statefp': integer, 'countyfp': integer, 'county_name_x': string, 'fips_code': integer, 'winning_party': string, 'State': string, 'Area_name': string,
#  'Civilian_labor_force_2012': integer, 'Employed_2012': integer, 'Unemployed_2012': integer, 'Unemployment_rate_2012': float,
#  'state_y': string, 'ansi_code': integer, 'county_name_y': string, 'population': integer, 'housing_units': integer, 'area_land_mt': integer, 'area_water_mt': integer,
#  'area_land_mi': float, 'area_water_mi': float, 'latitude': float, 'logitude': float, 'naics': integer, 'unions_count': integer,
#  'county_x': string, 'diabetes_count': integer, 'diabetes%': float, 'county_y': string, 'inactivity_count': integer, 'inactivity%': float,
#  'county_name': string, 'drug_deaths': integer]

# Map columns accordingly:
result = pd.DataFrame()

result['state_x'] = join_4['state_x'] if 'state_x' in join_4 else join_4['state']
result['statefp'] = join_4['statefp'].astype('Int64')
result['countyfp'] = join_4['countyfp'].astype('Int64')
result['county_name_x'] = join_4['county_name_x'] if 'county_name_x' in join_4 else join_4['county_name']
result['fips_code'] = join_4['fips_code'].astype('Int64')
result['winning_party'] = join_4['winning_party']
result['State'] = join_4['State']
result['Area_name'] = join_4['Area_name']
result['Civilian_labor_force_2012'] = join_4['Civilian_labor_force_2012'].astype('Int64')
result['Employed_2012'] = join_4['Employed_2012'].astype('Int64')
result['Unemployed_2012'] = join_4['Unemployed_2012'].astype('Int64')
result['Unemployment_rate_2012'] = join_4['Unemployment_rate_2012'].astype(float)
result['state_y'] = join_4['state_y'] if 'state_y' in join_4 else join_4['state']
result['ansi_code'] = join_4['ansi_code'].astype('Int64')
result['county_name_y'] = join_4['county_name_y'] if 'county_name_y' in join_4 else join_4['county_name']
result['population'] = join_4['population'].astype('Int64')
result['housing_units'] = join_4['housing_units'].astype('Int64')
result['area_land_mt'] = join_4['area_land_mt'].astype('Int64')
result['area_water_mt'] = join_4['area_water_mt'].astype('Int64')
result['area_land_mi'] = join_4['area_land_mi'].astype(float)
result['area_water_mi'] = join_4['area_water_mi'].astype(float)
result['latitude'] = join_4['latitude'].astype(float)
result['logitude'] = join_4['logitude'].astype(float)
result['naics'] = join_4['naics'].astype('Int64')
result['unions_count'] = join_4['unions_count'].astype('Int64')
result['county_x'] = join_4['county'] if 'county' in join_4 else join_4['county_x'] if 'county_x' in join_4 else None
result['diabetes_count'] = join_4['diabetes_count'].astype('Int64')
result['diabetes%'] = join_4['diabetes%'].astype(float)
result['county_y'] = join_4['county_y'] if 'county_y' in join_4 else join_4['county'] if 'county' in join_4 else None
result['inactivity_count'] = join_4['inactivity_count'].astype('Int64')
result['inactivity%'] = join_4['inactivity%'].astype(float)
result['county_name'] = join_4['county_name']
result['drug_deaths'] = join_4['drug_deaths'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_73/target_multisource_mcts.csv", index=False)