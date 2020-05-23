# Limpieza datos COVID

Este reposiorio contiene la data limpia de los datos abiertos de coronavirus publicada por el Estado peruano [en la plataforma de datos abiertos](https://www.datosabiertos.gob.pe/dataset/casos-positivos-por-covid-19-ministerio-de-salud-minsa/resource/690e57a6-a465-47d8-86fd) y los scripts para su reproducción.

La fecha de descarga de los datos es: `2020-05-23T14:00 (GMT-5)`. La limpieza no contiene datos que han sido añadidos con posterioridad.

Si deseas correr los scripts, sigue los siguientes pasos de instalación.

1. Clona este repositorio en tu computadora
2. Instala anaconda. Instrucciones [aquí](https://docs.anaconda.com/anaconda/install/mac-os/)
3. Crea un environment con todas las dependencias: `conda env create -f environment.yml`

Si solo deseas la data, puedes encontrarla en el folder `data/data_limpia_datos_covid_2020_05_22.csv`. Nota que a diferencia de la data original, la data límpia contiene una columna con el ubigeo de los distritos. Puedes usar esta información para cruzarla con otras bases de datos.

## Instrucciones para Pull Requests

Si deseas hacer un PR, por favor, usa el file `.py`y no lo hagas directamente en el notebook. Te recomiendo que para eso uses [jupytext](https://jupytext.readthedocs.io/en/latest/introduction.html).