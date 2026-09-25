import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_73/training_5.csv", index_col=0)

union_4_2 = pd.concat([s4, s2], ignore_index=True, sort=False)

join_1 = pd.merge(union_4_2, s0, how='inner', on='fips_code', suffixes=('_y', '_x'))

join_2 = pd.merge(join_1, s1, how='inner', on='fips_code')

join_3 = pd.merge(join_2, s3, how='inner', on='fips_code', suffixes=('_y', '_x'))

final = pd.merge(join_3, s5, how='inner', on='fips_code', suffixes=('_y', '_x'))

final['state_x'] = final['state_x'].astype(str)
final['statefp'] = final['statefp'].astype('Int64')
final['countyfp'] = final['countyfp'].astype('Int64')
final['county_name_x'] = final['county_name_x'].astype(str)
final['fips_code'] = final['fips_code'].astype('Int64')
final['winning_party'] = final['winning_party'].astype(str)
final['State'] = final['State'].astype(str)
final['Area_name'] = final['Area_name'].astype(str)
final['Civilian_labor_force_2012'] = final['Civilian_labor_force_2012'].astype('Int64')
final['Employed_2012'] = final['Employed_2012'].astype('Int64')
final['Unemployed_2012'] = final['Unemployed_2012'].astype('Int64')
final['Unemployment_rate_2012'] = final['Unemployment_rate_2012'].astype(float)
final['state_y'] = final['state_y'].astype(str)
final['ansi_code'] = final['ansi_code'].astype('Int64')
final['county_name_y'] = final['county_name_y'].astype(str)
final['population'] = final['population'].astype('Int64')
final['housing_units'] = final['housing_units'].astype('Int64')
final['area_land_mt'] = final['area_land_mt'].astype('Int64')
final['area_water_mt'] = final['area_water_mt'].astype('Int64')
final['area_land_mi'] = final['area_land_mi'].astype(float)
final['area_water_mi'] = final['area_water_mi'].astype(float)
final['latitude'] = final['latitude'].astype(float)
final['logitude'] = final['logitude'].astype(float)
final['naics'] = final['naics'].astype('Int64')
final['unions_count'] = final['unions_count'].astype('Int64')
final['county_x'] = final['county'].astype(str)
final['diabetes_count'] = final['diabetes_count'].astype('Int64')
final['diabetes%'] = final['diabetes%'].astype(float)
final['county_y'] = final['county'].astype(str)
final['inactivity_count'] = final['inactivity_count'].astype('Int64')
final['inactivity%'] = final['inactivity%'].astype(float)
final['county_name'] = final['county_name'].astype(str)
final['drug_deaths'] = final['drug_deaths'].astype('Int64')

result = final[['state_x', 'statefp', 'countyfp', 'county_name_x', 'fips_code', 'winning_party', 'State', 'Area_name',
                'Civilian_labor_force_2012', 'Employed_2012', 'Unemployed_2012', 'Unemployment_rate_2012',
                'state_y', 'ansi_code', 'county_name_y', 'population', 'housing_units', 'area_land_mt', 'area_water_mt',
                'area_land_mi', 'area_water_mi', 'latitude', 'logitude', 'naics', 'unions_count', 'county_x',
                'diabetes_count', 'diabetes%', 'county_y', 'inactivity_count', 'inactivity%', 'county_name', 'drug_deaths']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_73/target_multisource_mcts.csv", index=False)