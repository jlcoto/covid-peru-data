# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: 'Python 3.7.7 64-bit (''covid-hackaton'': conda)'
#     language: python
#     name: python37764bitcovidhackatoncondad02ba9ce9daa416ca3a7ed66f38a2896
# ---

# +
from collections import namedtuple

import numpy as np
import pandas as pd
import unidecode

# -

casos_df = pd.read_csv(
    "../data/original/datos_abiertos_siscovid_2020_05_22.csv",
    parse_dates=["FECHA_NACIMIENTO", "FECHA_PRUEBA"],
    encoding="latin",
)

ubigeo_df = pd.read_csv(
    "../data/original/ubigeo_distritos.csv", dtype={"ubigeo": "string"}
)


def col_a_minusculas(df):
    df.columns = [col.lower() for col in df.columns]


def uniformizar_data(df):
    """Quitar mayusculas y caracteres especiales como 
    tildes"""
    df[["departamento", "provincia", "distrito"]] = df[
        ["departamento", "provincia", "distrito"]
    ].applymap(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)
    df[["sexo", "departamento", "provincia", "distrito"]] = df[
        ["sexo", "departamento", "provincia", "distrito"]
    ].apply(lambda x: x.str.title().str.strip())
    return df


def helper_add_ubigeo(df, ubigeo_df):
    # Ayuda para unir localiazaciones con ubigeo
    # retorna los casos donde ubigeo no se encuentra
    # para uniformizar la data
    localizacion = (
        df.groupby(["departamento", "provincia", "distrito"], as_index=False)
        .count()
        .loc[:, ["departamento", "provincia", "distrito"]]
    )
    merge_ubigeos = localizacion.merge(
        ubigeo_df, how="left", on=["departamento", "provincia", "distrito"]
    )
    return merge_ubigeos.loc[merge_ubigeos.ubigeo.isnull()]


# +
Dcorreccion = namedtuple(
    "RemplazarDistrito", ["departamento", "provincia", "distrito", "cambio"]
)
Pcorreccion = namedtuple(
    "RemplazarDepartamento", ["departamento", "provincia", "cambio"]
)
# Casos para correcciones de diferencias entre distrito en la
# data y distrito en nuestra base de ubigeos
correcciones_dist = [
    ("Apurimac", "Chincheros", "Anco_Huallo", "Anco-Huallo"),
    (
        "Ayacucho",
        "Huamanga",
        "Andres Avelino Caceres",
        "Andres Avelino Caceres Dorregaray",
    ),
    ("Huanuco", "Huanuco", "Quisqui (Kichki)", "Quisqui"),
    ("Piura", "Sechura", "Rinconada Llicuar", "Rinconada-Llicuar"),
    ("San Martin", "Picota", "Caspisapa", "Caspizapa"),
    (
        "Tacna",
        "Tacna",
        "Coronel Gregorio Albarracin L.",
        "Coronel Gregorio Albarracin Lanchipa",
    ),
    ("Ucayali", "Atalaya", "Raymondi", "Raimondi"),
    (
        "Callao",
        "Prov. Const. Del Callao",
        "Carmen De La Legua Reynoso",
        "Carmen De La Legua-Reynoso",
    ),
    (
        "Ayacucho",
        "Huamanga",
        "Andres Avelino Caceres",
        "Andres Avelino Caceres Dorregaray",
    ),
    (
        "Ayacucho",
        "Huamanga",
        "Andres Avelino Caceres D.",
        "Andres Avelino Caceres Dorregaray",
    ),
    (
        "Tacna",
        "Tacna",
        "Coronel Gregorio Albarracin L.",
        "Coronel Gregorio Albarracin Lanchipa",
    ),
    (
        "Puno",
        "Sandia",
        "San Pedro De Putina Puncu",
        "San Pedro De Putina Punco",
    ),
    ("Ica", "Nazca", "Nazca", "Nasca"),
]

correcciones_prov = [
    ("Ica", "Nazca", "Nasca"),
    ("Callao", "Prov. Const. Del Callao", "Callao"),
    ("Ica", "Nazca", "Nasca"),
]


def corregir_distritos(df, correcciones):
    """Ayuda para remover diferencias en distritos y permitir
    mejor asociacion entre casos y ubigeo"""
    for correccion in correcciones:
        data_correccion = Dcorreccion(*correccion)
        df.loc[
            (df["departamento"] == data_correccion.departamento)
            & (df["provincia"] == data_correccion.provincia)
            & (df["distrito"] == data_correccion.distrito),
            "distrito",
        ] = data_correccion.cambio


def corregir_provincias(df, correcciones):
    """Ayuda para remover diferencias en provincias y permitir
    mejor asociacion entre casos y ubigeo"""
    for correccion in correcciones:
        data_correccion = Pcorreccion(*correccion)
        df.loc[
            (df["departamento"] == data_correccion.departamento)
            & (df["provincia"] == data_correccion.provincia),
            "provincia",
        ] = data_correccion.cambio


# -

# En algunos casos parece que los meses y dias se han introducido al revés
def cambiar_a_mes_dia(columna):
    return pd.to_datetime(columna.dt.strftime("%Y-%d-%m"), format="%Y-%m-%d")


# Cambiando mayusculas
casos_df.columns = [col.lower() for col in casos_df.columns]
casos_df[["sexo", "departamento", "provincia", "distrito"]] = casos_df[
    ["sexo", "departamento", "provincia", "distrito"]
].apply(lambda x: x.str.title().str.strip())


# Limpiando acentos para uniformizar data
casos_df[["departamento", "provincia", "distrito"]] = casos_df[
    ["departamento", "provincia", "distrito"]
].applymap(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)
ubigeo_df = ubigeo_df.applymap(
    lambda x: unidecode.unidecode(x) if isinstance(x, str) else x
)

# Casos de Callao se asigna departamento Callao
casos_df.loc[
    (casos_df.provincia == "Callao") & (casos_df.departamento == ""),
    "departamento",
] = "Callao"

# Ayuda para unir localiazaciones con ubigeo
localizacion = (
    casos_df.groupby(["departamento", "provincia", "distrito"], as_index=False)
    .count()
    .loc[:, ["departamento", "provincia", "distrito"]]
)
merge_ubigeos = localizacion.merge(
    ubigeo_df, how="left", on=["departamento", "provincia", "distrito"]
)

# +
# Correcciones en distritos y provincias para uniformizar nombres
Dcorreccion = namedtuple(
    "RemplazarDistrito", ["departamento", "provincia", "distrito", "cambio"]
)
Pcorreccion = namedtuple(
    "RemplazarDepartamento", ["departamento", "provincia", "cambio"]
)

correcciones_distrito = [
    ("Apurimac", "Chincheros", "Anco_Huallo", "Anco-Huallo"),
    (
        "Ayacucho",
        "Huamanga",
        "Andres Avelino Caceres",
        "Andres Avelino Caceres Dorregaray",
    ),
    ("Huanuco", "Huanuco", "Quisqui (Kichki)", "Quisqui"),
    ("Piura", "Sechura", "Rinconada Llicuar", "Rinconada-Llicuar"),
    ("San Martin", "Picota", "Caspisapa", "Caspizapa"),
    (
        "Tacna",
        "Tacna",
        "Coronel Gregorio Albarracin L.",
        "Coronel Gregorio Albarracin Lanchipa",
    ),
    ("Ucayali", "Atalaya", "Raymondi", "Raimondi"),
    (
        "Callao",
        "Prov. Const. Del Callao",
        "Carmen De La Legua Reynoso",
        "Carmen De La Legua-Reynoso",
    ),
]


for correccion in correcciones_distrito:
    data_correccion = Dcorreccion(*correccion)
    casos_df.loc[
        (casos_df["departamento"] == data_correccion.departamento)
        & (casos_df["provincia"] == data_correccion.provincia)
        & (casos_df["distrito"] == data_correccion.distrito),
        "distrito",
    ] = data_correccion.cambio


correcciones_provincia = [
    ("Callao", "Prov. Const. Del Callao", "Callao"),
    ("Ica", "Nazca", "Nasca"),
]

for correccion in correcciones_provincia:
    data_correccion = Pcorreccion(*correccion)
    casos_df.loc[
        (casos_df["departamento"] == data_correccion.departamento)
        & (casos_df["provincia"] == data_correccion.provincia),
        "provincia",
    ] = data_correccion.cambio

# -

casos_df = casos_df.merge(
    ubigeo_df, how="left", on=["departamento", "provincia", "distrito"]
)

duplicated_uuid = casos_df[
    casos_df.groupby("uuid")["uuid"].transform("size") > 1
]

# Ayudante para identificar id duplicados
dedup = duplicated_uuid.merge(duplicated_uuid, how="left", on="uuid")

# +
# Algunos casos que explican duplicados e inconsistencias en data

# Caso de fechas de nacimiento diferentes para mismo uuid sin missings
comp_nacimiento = dedup[
    (dedup.fecha_nacimiento_x.notnull())
    & (dedup.fecha_nacimiento_x != dedup.fecha_nacimiento_y)
]


# Casos donde mismo id es identificado como masculino y feminino
comp_fem_masc = dedup[
    (dedup.sexo_x.notnull() & dedup.sexo_y.notnull())
    & (dedup.sexo_x != dedup.sexo_y)
]


# Mismo id diferente departamento
comp_dpto = dedup[
    (dedup.departamento_x.notnull())
    & (dedup.departamento_x != dedup.departamento_y)
]


# Mismo id diferente provincia
comp_provincia = dedup[
    (dedup.provincia_x.notnull()) & (dedup.provincia_x != dedup.provincia_y)
]

# Mismo id diferente distrito
comp_distrito = dedup[
    (dedup.distrito_x.notnull()) & (dedup.distrito_x != dedup.distrito_y)
]

# Mismo id diferente fecha de prueba
comp_fecha_prueba = dedup[
    (dedup.tipo_prueba_x.notnull())
    & (dedup.fecha_prueba_x != dedup.fecha_prueba_y)
]
# -

# Para limpiar casos de dobles con misma id, nos quedamos con
# las observaciones que menos campos vacios tienen
casos_df["num_vacios"] = casos_df.isnull().sum(axis=1)
casos_df = casos_df.sort_values(
    by=["uuid", "num_vacios", "fecha_prueba"], ascending=[True, True, False]
)
casos_df = casos_df.groupby(["uuid"], as_index=False).first()
casos_df = casos_df.drop(columns="num_vacios")
casos_df.to_csv(
    "../data/limpia/data_limpia_datos_siscovid_2020_05_22.csv", index=False
)

# ### Nueva data 2020-05-24

data_05_24 = pd.read_csv(
    "../data/original/datos_abiertos_siscovid_2020_05_24.csv",
    parse_dates=["FECHA_RESULTADO"],
    encoding="latin",
    dtype={"EDAD": pd.Int64Dtype()},
)
data_05_24.columns = [col.lower() for col in data_05_24.columns]

# Uniformizando minusculas y limpiando caracteres especiales
data_05_24[["departamento", "provincia", "distrito"]] = data_05_24[
    ["departamento", "provincia", "distrito"]
].applymap(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)
data_05_24[["sexo", "departamento", "provincia", "distrito"]] = data_05_24[
    ["sexo", "departamento", "provincia", "distrito"]
].apply(lambda x: x.str.title().str.strip())

# +
# Correcciones en distritos y provincias para uniformizar nombres
Dcorreccion = namedtuple(
    "RemplazarDistrito", ["departamento", "provincia", "distrito", "cambio"]
)
Pcorreccion = namedtuple(
    "RemplazarDepartamento", ["departamento", "provincia", "cambio"]
)

correcciones_distrito = [
    (
        "Ayacucho",
        "Huamanga",
        "Andres Avelino Caceres",
        "Andres Avelino Caceres Dorregaray",
    ),
    (
        "Ayacucho",
        "Huamanga",
        "Andres Avelino Caceres D.",
        "Andres Avelino Caceres Dorregaray",
    ),
    (
        "Tacna",
        "Tacna",
        "Coronel Gregorio Albarracin L.",
        "Coronel Gregorio Albarracin Lanchipa",
    ),
    (
        "Puno",
        "Sandia",
        "San Pedro De Putina Puncu",
        "San Pedro De Putina Punco",
    ),
    ("Ica", "Nazca", "Nazca", "Nasca"),
]


for correccion in correcciones_distrito:
    data_correccion = Dcorreccion(*correccion)
    data_05_24.loc[
        (data_05_24["departamento"] == data_correccion.departamento)
        & (data_05_24["provincia"] == data_correccion.provincia)
        & (data_05_24["distrito"] == data_correccion.distrito),
        "distrito",
    ] = data_correccion.cambio


correcciones_provincia = [("Ica", "Nazca", "Nasca")]

for correccion in correcciones_provincia:
    data_correccion = Pcorreccion(*correccion)
    data_05_24.loc[
        (data_05_24["departamento"] == data_correccion.departamento)
        & (data_05_24["provincia"] == data_correccion.provincia),
        "provincia",
    ] = data_correccion.cambio

# Convertir data Region a Lima
data_05_24.loc[
    data_05_24.departamento == "Lima Region", "departamento"
] = "Lima"

# -

# Ayuda para unir localiazaciones con ubigeo
localizacion = (
    data_05_24.groupby(
        ["departamento", "provincia", "distrito"], as_index=False
    )
    .count()
    .loc[:, ["departamento", "provincia", "distrito"]]
)
merge_ubigeos = localizacion.merge(
    ubigeo_df, how="left", on=["departamento", "provincia", "distrito"]
)

data_05_24 = data_05_24.merge(
    ubigeo_df, how="left", on=["departamento", "provincia", "distrito"]
)

antes_primer_caso = data_05_24.fecha_resultado < "2020-03-06"
posteriores_fecha_data = data_05_24.fecha_resultado > "2020-05-24"
data_05_24.loc[antes_primer_caso, "fecha_resultado"] = cambiar_a_mes_dia(
    data_05_24.loc[antes_primer_caso, "fecha_resultado"]
)
data_05_24.loc[posteriores_fecha_data, "fecha_resultado"] = cambiar_a_mes_dia(
    data_05_24.loc[posteriores_fecha_data, "fecha_resultado"]
)
data_05_24 = data_05_24[
    (data_05_24.fecha_resultado >= "2020-03-06")
    | (data_05_24.fecha_resultado <= "2020-05-24")
    | (data_05_24.fecha_resultado.isnull())
]

data_05_24.to_csv(
    "../data/limpia/data_limpia_datos_siscovid_2020_05_24.csv", index=False
)

# ### Nueva data 2020-05-26

data_05_26 = pd.read_csv(
    "../data/original/datos_abiertos_siscovid_2020_05_26.csv",
    parse_dates=["FECHA_RESULTADO"],
    encoding="latin",
    dtype={"EDAD": pd.Int64Dtype()},
)

col_a_minusculas(data_05_26)

data_05_26 = uniformizar_data(data_05_26)

corregir_distritos(data_05_26, correcciones_dist)

corregir_provincias(data_05_26, correcciones_prov)

antes_primer_caso = data_05_26.fecha_resultado < "2020-03-06"
posteriores_fecha_data = data_05_26.fecha_resultado > "2020-05-26"
data_05_26.loc[antes_primer_caso, "fecha_resultado"] = cambiar_a_mes_dia(
    data_05_26.loc[antes_primer_caso, "fecha_resultado"]
)
data_05_26.loc[posteriores_fecha_data, "fecha_resultado"] = cambiar_a_mes_dia(
    data_05_26.loc[posteriores_fecha_data, "fecha_resultado"]
)
data_05_26 = data_05_26[
    (data_05_26.fecha_resultado >= "2020-03-06")
    | (data_05_26.fecha_resultado <= "2020-05-24")
    | (data_05_26.fecha_resultado.isnull())
]

data_05_26.to_csv(
    "../data/limpia/data_limpia_datos_siscovid_2020_05_26.csv", index=False
)
