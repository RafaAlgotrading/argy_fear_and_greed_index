import requests
import datetime as dt
import pandas as pd


def specific_request(id, from_date, up_to_date):
    request = requests.get(
        bcra_specific_url + f'{id}/{from_date}/{up_to_date}',
        verify=False
    ).json()['results']

    return request


# ========================= ENDPOINTS =========================
bcra_url = "https://api.bcra.gob.ar/estadisticas/v1/principalesvariables"
bcra_specific_url = "https://api.bcra.gob.ar/estadisticas/v1/datosvariable/"


# ========================= PROGRAMA PRINCIPAL =========================
bcra_request = requests.get(bcra_url, verify=False).json()["results"]

ids = [var["idVariable"] for var in bcra_request]
variables = [var["descripcion"] for var in bcra_request]

ids_variables = dict(zip(ids, variables))


january = '2024-01-01'
today_date = dt.datetime.now().date()

all_variables_df = pd.DataFrame()
all_variables_df["fecha"] = pd.bdate_range(january, today_date)


# Si lo dejo las comas en el, no puedo transformarlo a float
# Lo paso a float y puedo ver las variables resaltadas en color segun valor

# Podría hacer diff e if para chequear si hay valores desordenados, pero
# pederíamos eficiencia por escribir y ejecutar más código. Aplicandolo
# directo nos aseguramos que va a estar ordenado. Algo así:

#df_by_id['time_difference'] = df_by_id['fecha'].diff()
# for time_diff in df_by_id['time_difference']:
#     if time_diff > time_diff - :
#         print(time_diff)


# 'id' toma los valores, no lo indices
for id in ids:
    url_id = bcra_specific_url + f"{id}/{january}/{today_date}"
    request = requests.get(url_id, verify=False).json()["results"]
    df_by_id = pd.DataFrame(request)[["fecha", "valor"]]
    df_by_id.rename(columns={'valor': id}, inplace=True)
    df_by_id[id] = df_by_id[id].str.replace(".", "")
    df_by_id[id] = df_by_id[id].str.replace(",", ".")
    df_by_id[id] = df_by_id[id].astype(float)
    df_by_id["fecha"] = pd.to_datetime(df_by_id["fecha"], format='%d/%m/%Y')

    df_by_id = df_by_id.sort_values('fecha').reset_index(drop=True)

    df_by_id = df_by_id[~df_by_id["fecha"].dt.dayofweek.isin(
        [5, 6]
    )].reset_index(drop=True)
    all_variables_df = pd.merge(
        all_variables_df,
        df_by_id,
        on="fecha",
        how="outer")


# Indicadores que puedan seguir, valga la redundancia, indicando
# momentum positivo para el país y el mercado.

# ej. inflación -mensual, interanual, esperada-, reservas bcra, pases pasivos
# ¿tasas de interes?, ¿tipo de cambio?

# ej. La inflación de ahora, es menor que la del mes pasado?
# Voy haciendo un track record de los % de inflación.


# Podemos hacer un fear & greed index, basado en estas variables


# Devuelve directamente los valores
# for var in bcra_request:
#     for data in var:
    # print(var[data])


# Devuelve también el nombre de las variables
# for var in bcra_request: #Toma elemento por elemento
#     for key, value in var.items(): #Esto se aplica solo a diccionarios.
#         print(key, value)


# print(
#       f"La inflación mensual del mes de {meses[mes]}" +
#       f" es de {inflacion_mensual[meses[mes]]}%"
#       )


# 27//2024-06-11
# january = '2024-01-01'
# today_date = dt.datetime.now().date()


# inflaciones_mensuales = specific_request(27, january, today_date)
# reservas_int_mensuales = specific_request(1, january, today_date)


# meses = {
#     1:"Enero", 2: "Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio",
#     7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre",
#     12:"Diciembre"
#          }

# inflacion_mensual = {}

# mes = 1
# for dato_inflacion in inflaciones_mensuales:
#     inflacion_mensual[meses[mes]] = dato_inflacion['valor']+'%'
#     mes+=1


# #Si hago el fear & greed index con todas estas variables, seguramente
# # también necesiten cierta ponderación.
# fandg_index_list = []

# fandg_index = {

#     }
