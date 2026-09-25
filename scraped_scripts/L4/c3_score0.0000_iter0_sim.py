import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_3/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_3/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_3/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_3/training_3.csv", index_col=0)

join_1 = pd.merge(s1, s2, how="inner", on="COD_PERSONA")
join_2 = pd.merge(join_1, s3, how="inner", on="COD_IDCONTRA")
join_3 = pd.merge(join_2, s0, how="inner", on="COD_OFICI")

df = join_3.rename(columns={
    "COD_PERSONA": "COD_PERSONA",
    "estado_cli": "estado_cli",
    "COD_AREANEGO": "COD_AREANEGO",
    "COD_EDAD": "COD_EDAD",
    "COD_OFICIPAL": "COD_OFICIPAL",
    "COD_SEGLOBAL": "COD_SEGLOBAL",
    "COD_OFICI": "COD_OFICI",
    "COD_NIVELOFIC": "COD_NIVELOFIC",
    "des_ofici": "des_ofici",
    "cod_cbc": "cod_cbc",
    "des_cbc": "des_cbc",
    "cod_zona": "cod_zona",
    "des_zona": "des_zona",
    "COD_TERRIT": "COD_TERRIT",
    "des_territ": "des_territ",
    "cod_areanego": "cod_areanego",
    "des_areanego": "des_areanego",
    "COD_IDCONTRA": "COD_IDCONTRA",
    "XTI_ESTADO": "XTI_ESTADO",
    "QNU_ORDTIT": "QNU_ORDTIT",
    "FAP_CONTR": "FAP_CONTR",
    "IMP_CAPDIS": "IMP_CAPDIS",
    "IMP_CAPINI": "IMP_CAPINI",
    "IMP_CAPPEN": "IMP_CAPPEN",
})

df["COD_PERSONA_x"] = df["COD_PERSONA_x"] if "COD_PERSONA_x" in df else df["COD_PERSONA"]
df["COD_PERSONA_y"] = df["COD_PERSONA_y"] if "COD_PERSONA_y" in df else df["COD_PERSONA"]

df = df[[
    "COD_INTERV",
    "estado_cli",
    "COD_PERSONA",
    "COD_AREANEGO",
    "COD_EDAD",
    "COD_OFICIPAL",
    "COD_SEGLOBAL",
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
    "FAP_CONTR",
    "IMP_CAPDIS",
    "IMP_CAPINI",
    "IMP_CAPPEN",
    "COD_PERSONA_y",
    "XTI_ESTADO",
    "QNU_ORDTIT"
]]

for col in ["COD_PERSONA", "COD_AREANEGO", "COD_EDAD", "COD_OFICIPAL", "COD_SEGLOBAL", "COD_OFICI", "COD_NIVELOFIC",
            "des_ofici", "cod_cbc", "des_cbc", "cod_zona", "des_zona", "COD_TERRIT", "des_territ", "cod_areanego",
            "des_areanego", "COD_IDCONTRA", "COD_PERSONA_x", "FAP_CONTR", "IMP_CAPDIS", "IMP_CAPINI", "IMP_CAPPEN",
            "COD_PERSONA_y", "XTI_ESTADO", "QNU_ORDTIT"]:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_3/target_multisource_mcts.csv", index=False)