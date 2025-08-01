import pandas as pd
import numpy as np

# Load source tables (skip first column which is index)
src0 = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length4_2/test_0.csv"
).iloc[:, 1:]
src1 = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length4_2/test_1.csv"
).iloc[:, 1:]
src2 = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length4_2/test_2.csv"
).iloc[:, 1:]
src3 = pd.read_csv(
    "autopipeline-benchmarks/github-pipelines/length4_2/test_3.csv"
).iloc[:, 1:]

# Operation 1: JOIN Source4_2_2 and Source4_2_3 on ["COD_IDCONTRA", "COD_IDCONTRA"]
df = pd.merge(
    src2,
    src3,
    left_on="COD_IDCONTRA",
    right_on="COD_IDCONTRA",
    how="inner",
    suffixes=("_x", "_y"),
)

# Operation 2: JOIN Source4_2_0 and Source4_2_1 on ["COD_OFICIPAL", "COD_OFICI"]
df0_1 = pd.merge(
    src0,
    src1,
    left_on="COD_OFICIPAL",
    right_on="COD_OFICI",
    how="inner",
    suffixes=("", "_1"),
)

# Operation 3: JOIN Source4_2_2 and Source4_2_0 on ["COD_PERSONA", "COD_PERSONA"]
df2_0 = pd.merge(
    df,
    src0,
    left_on="COD_PERSONA_x",
    right_on="COD_PERSONA",
    how="inner",
    suffixes=("", "_0"),
)

df_final = pd.merge(
    df2_0,
    df0_1[
        ["COD_OFICIPAL"]
        + [c for c in df0_1.columns if c not in src0.columns and c != "COD_OFICIPAL"]
    ],
    on="COD_OFICIPAL",
    how="inner",
)

# Prepare final dataframe with target schema:
final_df = pd.DataFrame()

final_df["FAP_CONTR"] = df_final["FAP_CONTR"]
final_df["COD_PERSONA"] = df_final["COD_PERSONA_x"]
final_df["COD_AREANEGO"] = df_final["COD_AREANEGO"]
final_df["COD_EDAD"] = df_final["COD_EDAD"]
final_df["COD_OFICIPAL"] = df_final["COD_OFICIPAL"]
final_df["COD_SEGLOBAL"] = df_final["COD_SEGLOBAL"]
final_df["estado_cli"] = df_final["estado_cli"]

final_df["COD_OFICI"] = df_final["COD_OFICI"]
final_df["COD_NIVELOFIC"] = df_final["COD_NIVELOFIC"]
final_df["des_ofici"] = df_final["des_ofici"]
final_df["cod_cbc"] = df_final["cod_cbc"]
final_df["des_cbc"] = df_final["des_cbc"]
final_df["cod_zona"] = df_final["cod_zona"]
final_df["des_zona"] = df_final["des_zona"]
final_df["COD_TERRIT"] = df_final["COD_TERRIT"]
final_df["des_territ"] = df_final["des_territ"]
final_df["cod_areanego"] = df_final["cod_areanego"]
final_df["des_areanego"] = df_final["des_areanego"]

final_df["COD_IDCONTRA"] = df_final["COD_IDCONTRA"]
final_df["COD_PERSONA_x"] = df_final["COD_PERSONA_x"]

final_df["IMP_CAPDIS"] = df_final["IMP_CAPDIS"]
final_df["IMP_CAPINI"] = df_final["IMP_CAPINI"]
final_df["IMP_CAPPEN"] = df_final["IMP_CAPPEN"]

final_df["COD_PERSONA_y"] = df_final["COD_PERSONA_y"]
final_df["XTI_ESTADO"] = df_final["XTI_ESTADO"]
final_df["QNU_ORDTIT"] = df_final["QNU_ORDTIT"]
final_df["COD_INTERV"] = df_final["COD_INTERV"]


# Convert dates in FAP_CONTR to uppercase string like examples (e.g. '20MAY2005')
def convert_date_fmt(date_str):
    try:
        dt = pd.to_datetime(date_str, format="%d%b%Y", errors="coerce")
        if pd.isna(dt):
            return date_str.upper()
        return (
            dt.strftime("%d").lstrip("0")
            + dt.strftime("%b").upper()
            + dt.strftime("%Y")
        )
    except:
        return date_str.upper()


final_df["FAP_CONTR"] = final_df["FAP_CONTR"].astype(str).apply(convert_date_fmt)

# Apply group by according to Criticizer Response:
group_cols = ["FAP_CONTR"]
agg_cols = [
    "COD_PERSONA",
    "COD_AREANEGO",
    "COD_EDAD",
    "COD_OFICIPAL",
    "COD_SEGLOBAL",
    "estado_cli",
    "COD_OFICI",
    "COD_NIVELOFIC",
    "des_ofici",
    "cod_cbc",
    "des_cbc",
    "cod_zona",
    "des_zona",
    "COD_TERRIT",
    "des_territ",
    "cod_areanego",
    "des_areanego",
    "COD_IDCONTRA",
    "COD_PERSONA_x",
    "IMP_CAPDIS",
    "IMP_CAPINI",
    "IMP_CAPPEN",
    "COD_PERSONA_y",
    "XTI_ESTADO",
    "QNU_ORDTIT",
    "COD_INTERV",
]

# For count aggregation on all agg_cols, we count occurrences (count non-null values)
agg_dict = {col: "count" for col in agg_cols}

grouped_df = final_df.groupby(group_cols).agg(agg_dict).reset_index()

# Make sure columns order consistent with final_df but only cols in grouped_df
final_col_order = ["FAP_CONTR"] + agg_cols

grouped_df = grouped_df[final_col_order]

# Write output file
grouped_df.to_csv(
    "autopipeline-benchmarks/github-pipelines/length4_2/target_multisource_critique_hard.csv",
    index=False,
)
