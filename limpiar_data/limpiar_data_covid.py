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
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from collections import namedtuple

import numpy as np
import pandas as pd
import unidecode
# -

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

casos_df = pd.read_csv('data/DATOSABIERTOS_SISCOVID.csv',
                       parse_dates=['FECHA_NACIMIENTO', 'FECHA_PRUEBA'],
                       encoding = "latin")

ubigeo_df = pd.read_csv('data/ubigeo.csv', dtype={'ubigeo': 'string'})

# Cambiando mayusculas
casos_df.columns = [col.lower() for col in casos_df.columns]
casos_df[['sexo', 'departamento', 'provincia', 'distrito']] = casos_df[['sexo',
                                                                        'departamento',
                                                                        'provincia',
                                                                        'distrito']].apply(lambda x: x.str.title().str.strip())


# Limpiando acentos para uniformizar data
casos_df[['departamento', 'provincia', 'distrito']] = casos_df[['departamento', 'provincia', 'distrito']].applymap(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)
ubigeo_df = ubigeo_df.applymap(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)

# Casos de Callao se asigna departamento Callao
casos_df.loc[(casos_df.provincia == 'Callao') & 
               (casos_df.departamento == ''), 'departamento'] = 'Callao'

# Ayuda para unir localiazaciones con ubigeo
localizacion = casos_df.groupby(['departamento', 'provincia', 'distrito'],
                 as_index=False).count().loc[:, ['departamento', 'provincia', 'distrito']]
merge_ubigeos = localizacion.merge(ubigeo_df, how='left',
                   on=['departamento', 'provincia', 'distrito'])

# +
# Correcciones en distritos y provincias para uniformizar nombres
Dcorreccion = namedtuple('RemplazarDistrito', ['departamento', 'provincia', 'distrito',  'cambio'])
Pcorreccion = namedtuple('RemplazarDepartamento', ['departamento', 'provincia', 'cambio'])

correcciones_distrito = [('Apurimac', 'Chincheros', 'Anco_Huallo', 'Anco-Huallo'),
                         ('Ayacucho', 'Huamanga', 'Andres Avelino Caceres', 'Andres Avelino Caceres Dorregaray'),
                         ('Huanuco', 'Huanuco', 'Quisqui (Kichki)', 'Quisqui'),
                        ('Piura', 'Sechura', 'Rinconada Llicuar', 'Rinconada-Llicuar'),
                        ('San Martin', 'Picota', 'Caspisapa', 'Caspizapa'),
                        ('Tacna', 'Tacna', 'Coronel Gregorio Albarracin L.', 'Coronel Gregorio Albarracin Lanchipa'),
                        ('Ucayali', 'Atalaya', 'Raymondi', 'Raimondi'),
                        ('Callao', 'Prov. Const. Del Callao', 'Carmen De La Legua Reynoso', 'Carmen De La Legua-Reynoso')]


for correccion in correcciones_distrito:
    data_correccion = Dcorreccion(*correccion)
    casos_df.loc[(casos_df['departamento']==data_correccion.departamento) &
                 (casos_df['provincia']==data_correccion.provincia) &
                (casos_df['distrito']==data_correccion.distrito), 'distrito']  = data_correccion.cambio  
    
    
correcciones_provincia = [('Callao', 'Prov. Const. Del Callao', 'Callao'),
                          ('Ica', 'Nazca', 'Nasca')]

for correccion in correcciones_provincia:
    data_correccion = Pcorreccion(*correccion)
    casos_df.loc[(casos_df['departamento']==data_correccion.departamento) &
                 (casos_df['provincia']==data_correccion.provincia), 'provincia']  = data_correccion.cambio  

# -

casos_df = casos_df.merge(ubigeo_df, how='left',
                   on=['departamento', 'provincia', 'distrito'])

duplicated_uuid = casos_df[casos_df.groupby('uuid')['uuid'].transform('size') > 1]

# Ayudante para identificar id duplicados
dedup = duplicated_uuid.merge(duplicated_uuid, how='left', on='uuid')

# +
# Algunos casos que explican duplicados e inconsistencias en data

# Caso de fechas de nacimiento diferentes para mismo uuid sin missings
comp_nacimiento = dedup[(dedup.fecha_nacimiento_x.notnull()) &(dedup.fecha_nacimiento_x != dedup.fecha_nacimiento_y)]


# Casos donde mismo id es identificado como masculino y feminino
comp_fem_masc = dedup[(dedup.sexo_x.notnull() & dedup.sexo_y.notnull()) & 
                       (dedup.sexo_x != dedup.sexo_y)]


# Mismo id diferente departamento
comp_dpto = dedup[(dedup.departamento_x.notnull()) &(dedup.departamento_x != dedup.departamento_y)]


# Mismo id diferente provincia
comp_provincia = dedup[(dedup.provincia_x.notnull()) & (dedup.provincia_x != dedup.provincia_y)]

# Mismo id diferente distrito
comp_distrito = dedup[(dedup.distrito_x.notnull()) &
      (dedup.distrito_x != dedup.distrito_y) ]

# Mismo id diferente fecha de prueba
comp_fecha_prueba = dedup[(dedup.tipo_prueba_x.notnull()) &(dedup.fecha_prueba_x != dedup.fecha_prueba_y)]
# -

# Para limpiar casos de dobles con misma id, nos quedamos con
# las observaciones que menos campos vacios tienen
casos_df['num_vacios'] = casos_df.isnull().sum(axis=1)
casos_df = casos_df.sort_values(by=['uuid', 'num_vacios', 'fecha_prueba'])
casos_df = casos_df.groupby(['uuid'], as_index=False).first()
casos_df = casos_df.drop(columns='num_vacios')
casos_df.to_csv('data/data_limpia_datos_covid_2020_05_22.csv', index=False)
