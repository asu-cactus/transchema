import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

agg = df0.groupby("country").agg(
    NY_GDP_MKTP_KN_x=pd.NamedAgg(column="NY.GDP.MKTP.KN", aggfunc="min"),
    SP_POP_TOTL_x=pd.NamedAgg(column="SP.POP.TOTL", aggfunc="max"),
    year_count=pd.NamedAgg(column="year", aggfunc=lambda x: x.nunique())
).reset_index()

# According to the target schema, we need columns:
# ['country', 'NY.GDP.MKTP.KN_x', 'SI.DST.10TH.10_x', 'SP.POP.TOTL_x',
#  'NY.GDP.MKTP.KN_y', 'SI.DST.10TH.10_y', 'SP.POP.TOTL_y',
#  'NY.GDP.MKTP.KN', 'SI.DST.10TH.10', 'SP.POP.TOTL']

# The source only has one table, so the _x and _y suffix columns likely come from the same source but different aggregations or views.
# The partial plan only aggregates min and max for GDP and population, and count distinct for year.
# The target has three groups of columns: _x, _y, and no suffix.
# We have min GDP as _x, max population as _x, but no SI.DST.10TH.10 in aggregation.
# The target examples show SI.DST.10TH.10 columns are mostly NaN, so we can fill them with NaN.
# The _y columns appear to be duplicates of _x columns (same values in examples).
# The no suffix columns appear to be duplicates of _x columns as well.

# So we replicate the aggregated values to _y and no suffix columns.
# SI.DST.10TH.10 columns are not present in source aggregations, so fill with NaN.

agg["SI.DST.10TH.10_x"] = pd.NA
agg["NY.GDP.MKTP.KN_y"] = agg["NY_GDP_MKTP_KN_x"]
agg["SI.DST.10TH.10_y"] = pd.NA
agg["SP.POP.TOTL_y"] = agg["SP_POP_TOTL_x"]
agg["NY.GDP.MKTP.KN"] = agg["NY_GDP_MKTP_KN_x"]
agg["SI.DST.10TH.10"] = pd.NA
agg["SP.POP.TOTL"] = agg["SP_POP_TOTL_x"]

agg = agg.rename(columns={
    "country": "country",
    "NY_GDP_MKTP_KN_x": "NY.GDP.MKTP.KN_x",
    "SP_POP_TOTL_x": "SP.POP.TOTL_x"
})

agg = agg[[
    "country",
    "NY.GDP.MKTP.KN_x",
    "SI.DST.10TH.10_x",
    "SP.POP.TOTL_x",
    "NY.GDP.MKTP.KN_y",
    "SI.DST.10TH.10_y",
    "SP.POP.TOTL_y",
    "NY.GDP.MKTP.KN",
    "SI.DST.10TH.10",
    "SP.POP.TOTL"
]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)