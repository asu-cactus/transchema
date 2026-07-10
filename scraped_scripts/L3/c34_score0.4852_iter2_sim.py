import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_34/training_1.csv", index_col=0)

agg0 = df0.groupby(['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'])[
    ['1960','1970','1980','1990','2000','2010']].mean().reset_index()

agg1 = df1.groupby(['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'])[
    ['1960','1970','1980','1990','2000','2010']].mean().reset_index()

# Filter agg0 for Rural population indicator
rural_indicators = agg0['Indicator Name'].unique()
agg0_rural = agg0[agg0['Indicator Name'].str.contains('Rural population', case=False, na=False)].copy()

# Filter agg1 for Electricity access indicator
elec_indicators = agg1['Indicator Name'].unique()
agg1_elec = agg1[agg1['Indicator Name'].str.contains('Access to electricity', case=False, na=False)].copy()

# Melt both aggregated tables to long format
rural_melt = agg0_rural.melt(id_vars=['Country Name', 'Country Code'], 
                             value_vars=['1960','1970','1980','1990','2000','2010'],
                             var_name='Year', value_name='Rural Value')

elec_melt = agg1_elec.melt(id_vars=['Country Name', 'Country Code'], 
                           value_vars=['1960','1970','1980','1990','2000','2010'],
                           var_name='Year', value_name='Electricity Value')

# Merge on Country Name, Country Code, Year
merged = pd.merge(rural_melt, elec_melt, on=['Country Name', 'Country Code', 'Year'], how='outer')

# Convert Year to string (already string from melt, but ensure)
merged['Year'] = merged['Year'].astype(str)

# Convert values to string as target schema requires string type
merged['Rural Value'] = merged['Rural Value'].astype(str)
merged['Electricity Value'] = merged['Electricity Value'].astype(str)

result = merged[['Country Name', 'Country Code', 'Year', 'Rural Value', 'Electricity Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_34/target_multisource_mcts.csv", index=False)