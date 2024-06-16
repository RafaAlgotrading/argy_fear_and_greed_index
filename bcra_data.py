import requests
import datetime as dt
import pandas as pd
import numpy as np


def specific_request(id, from_date, up_to_date):
    request = requests.get(
        bcra_specific_url + f'{id}/{from_date}/{up_to_date}',
        verify=False
    ).json()['results']

    return request

# ============================== FUNCIONES ==============================
def normalize(all_v_df):
    #Para evitar la columna fecha puedo dropearla por el momento o validarla
    # en un if. Quizá lo mejor es validarla, para así devolver un df
    # normalizado con ella y no tener que tratar de agregarlo en otro momento.
    #all_variables_df.drop('fecha', axis=1)
    df = all_v_df.copy()
    for column in df:
        if type(column) == int:
            df[column] = (
                df[column] - df[column].min()
                          ) / (df[column].max() - df[column].min()) * 100 
                
    return df  #series - series.min()) / (series.max() - series.min()) * 100
            
def invert(all_normalized_df, variables_to_invert):
    normalized_df = all_normalized_df.copy()
    for id_var in variables_to_invert:
        print(id_var)
        normalized_df[id_var] = 100 - normalized_df[id_var] 
        
        
    return normalized_df
        
# ============================== ENDPOINTS ==============================
bcra_url = "https://api.bcra.gob.ar/estadisticas/v2.0/PrincipalesVariables"
bcra_specific_url = "https://api.bcra.gob.ar/estadisticas/v2.0/DatosVariable/"



# ========================= PROGRAMA PRINCIPAL =========================
bcra_request = requests.get(bcra_url, verify=False).json()["results"]

ids = [var["idVariable"] for var in bcra_request]
vars_names = [var["descripcion"] for var in bcra_request]

ids_variables = dict(zip(ids, vars_names))


january = '2024-01-01'
today_date = dt.datetime.now().date()

all_variables_df = pd.DataFrame()
all_variables_df["fecha"] = pd.bdate_range(january, today_date)


# 'id' toma los valores, no lo indices
for id in ids:
    url_id = bcra_specific_url + f"{id}/{january}/{today_date}"
    #print(id, january, today_date)
    #url_id = "https://api.bcra.gob.ar/estadisticas/v2.0/DatosVariable/1/2024-01-01/2024-06-01"

    request = requests.get(url_id, verify=False).json()['results']
    df_by_id = pd.DataFrame(request)[["fecha", "valor"]]
    #print("Acá va el largo de cada serie: ", len(df_by_id['valor']))
    df_by_id.rename(columns={'valor': id}, inplace=True)
    
    
    df_by_id["fecha"] = pd.to_datetime(df_by_id["fecha"], format='%Y/%m/%d')

    #No se puede aplicar porque también hay una columna fecha peeero
    # podríamos sacarla/separarla momentaneamente.    
    #df_by_id = df_by_id.sort_index(axis=1).reset_index(drop=True)
    df_by_id = df_by_id.sort_values('fecha').reset_index(drop=True)

    #Saco los días sabado, domingos.
    df_by_id = df_by_id[~df_by_id["fecha"].dt.dayofweek.isin(
          [5, 6]
    )].reset_index(drop=True)
    
    all_variables_df = pd.merge(
         all_variables_df,
         df_by_id,
         on="fecha",
         how="outer")


#Itero la lista ids (tomo el valor del elemento, no el índice)
#Sobre la serie del 'id'--> df[id], tomo el último valor valido de esta. 
last_values = []
for id in ids:
    #Claro, la primera parte 'df[id]' es una serie...entonces, en la segunda
    # me tira el 'id' del último válido para poder acceder a el
    lv = all_variables_df[id][all_variables_df[id].last_valid_index()]
    last_values.append(lv)


#ponderaciones = pd.Series()
ponderaciones = [
    0.05,  # Reservas Internacionales del BCRA (en millones de dólares)
    0.03,  # Tipo de Cambio Minorista ($ por USD)
    0.03,  # Tipo de Cambio Mayorista ($ por USD)
    0.04,  # Tasa de Política Monetaria (en % n.a.)
    0.02,  # BADLAR en pesos de bancos privados (en % n.a.)
    0.02,  # TM20 en pesos de bancos privados (en % n.a.)
    0.02,  # Tasas de interés de las operaciones de pase activas para el BCRA, a 1 día de plazo (en % n.a.)
    0.02,  # Tasas de interés de las operaciones de pase pasivas para el BCRA, a 1 día de plazo (en % n.a.)
    0.02,  # Tasas de interés por préstamos entre entidades financieras privadas (BAIBAR) (en % n.a.)
    0.02,  # Tasas de interés por depósitos a 30 días de plazo en entidades financieras (en % n.a.)
    0.02,  # Tasa de interés de préstamos por adelantos en cuenta corriente
    0.02,  # Tasa de interés de préstamos personales
    0.04,  # Base monetaria - Total (en millones de pesos)
    0.03,  # Circulación monetaria (en millones de pesos)
    0.02,  # Billetes y monedas en poder del público (en millones de pesos)
    0.02,  # Efectivo en entidades financieras (en millones de pesos)
    0.02,  # Depósitos de los bancos en cta. cte. en pesos en el BCRA (en millones de pesos)
    0.02,  # Depósitos en efectivo en las entidades financieras - Total (en millones de pesos)
    0.02,  # En cuentas corrientes (neto de utilización FUCO) (en millones de pesos)
    0.02,  # En Caja de ahorros (en millones de pesos)
    0.03,  # A plazo (incluye inversiones y excluye CEDROS) (en millones de pesos)
    0.03,  # M2 privado, promedio móvil de 30 días, variación interanual (en %)
    0.03,  # Préstamos de las entidades financieras al sector privado (en millones de pesos)
    0.04,  # Inflación mensual (variación en %)
    0.04,  # Inflación interanual (variación en % i.a.)
    0.03,  # Inflación esperada - REM próximos 12 meses - MEDIANA (variación en % i.a)
    0.01,  # CER (Base 2.2.2002=1)
    0.01,  # Unidad de Valor Adquisitivo (UVA) (en pesos -con dos decimales-, base 31.3.2016=14.05)
    0.01,  # Unidad de Vivienda (UVI) (en pesos -con dos decimales-, base 31.3.2016=14.05)
    0.04,  # Tasa de Política Monetaria (en % e.a.)
    0.02,  # BADLAR en pesos de bancos privados (en % e.a.)
    0.01,  # Índice para Contratos de Locación (ICL-Ley 27.551, con dos decimales, base 30.6.20=1)
    0.02,  # Tasas de interés de las operaciones de pase pasivass para el BCRA, a 1 día de plazo (en % e.a.)
    0.02   # Pases pasivos para el BCRA - Saldos (en millones de pesos)
]#Se crea como una lista


#Solo con un retorno de la fórmula de normalize, lo cúal nos ahorraría algunas
#lineas de código, podemos hacer esto:
    
#all_variables_normalized = normalize.drop('fecha').apply(normalize)
all_normalized_variables = normalize(all_variables_df)


normalized_variables_to_invert = {
    4: 'Tipo de Cambio Minorista ($ por USD) Comunicación B 9791 - Promedio vendedor',
    5: 'Tipo de Cambio Mayorista ($ por USD) Comunicación A 3500 - Referencia',
    9: 'Tasas de interés de las operaciones de pase activas para el BCRA, a 1 día de plazo (en % n.a.)',
    10: 'Tasas de interés de las operaciones de pase pasivas para el BCRA, a 1 día de plazo (en % n.a.)',
    11: 'Tasas de interés por préstamos entre entidades financieras privadas (BAIBAR) (en % n.a.)',
    12: 'Tasas de interés por depósitos a 30 días de plazo en entidades financieras (en % n.a.)',
    13: 'Tasa de interés de préstamos por adelantos en cuenta corriente',
    14: 'Tasa de interés de préstamos personales',
    31: 'Índice para Contratos de Locación (ICL-Ley 27.551, con dos decimales, base 30.6.20=1)',
    41: 'Tasas de interés de las operaciones de pase pasivas para el BCRA, a 1 día de plazo (en % e.a.)',
    42: 'Pases pasivos para el BCRA - Saldos (en millones de pesos)'
}

all_normalized_and_inverted_variables = invert(
     all_normalized_variables,
     normalized_variables_to_invert
     )

datetime_to_merge = pd.DataFrame()
datetime_to_merge = all_normalized_and_inverted_variables['fecha']
all_normalized_and_inverted_variables.drop(['fecha'], axis=1,inplace = True)

get_out_datetime = all_normalized_and_inverted_variables

#Tengo muchos valores en NaN por lo que la multiplicación de estos con las
#   ponderaciones, nunca hubiera sido posible. Así, las lleno con la media.
#Aunque primeramente tengo, al menos una fila (la primera), donde hay muchisimo
# predominio de NaN por sobre valores (que de hecho eran 0). Así que primero
# debería ver cómo eliminar las filas donde esto prevalezca.
#Cambiarlo por 0's no creo que sea lo más adecuado porque luego voy a querer
# cambiarlos por la media

#Si le pongo 0 varios valores me tiran número muy bajos. Así también a nivel
# general.
#Si le pongo la media, los valores se inflan mucho donde no hay nada...

#Podríamos crear una func para que devuelva el indice en ambas formas o
# donde valga 0, buscar llenarlo con el previo último valor válido.
get_out_datetime = get_out_datetime.fillna(get_out_datetime.mean())

get_out_datetime[
    'fear_and_greed_index'
    ] = get_out_datetime.apply(
        lambda row: np.dot(row, ponderaciones),
        axis=1)

#No hago merge, hago concat porque para merge no tengo variable que confluya.
final_df = pd.concat([datetime_to_merge, get_out_datetime], axis=1)









# index = []
# for indexkey in ids_variables:
#     index.append(indexkey)

# index = pd.Series(index)

# seviene = pd.DataFrame()
# seviene['ids'] = index



#ids_variables_df = pd.DataFrame(ids_variables, index=index)

#ponderaciones = pd.Series(ponderaciones)



# vars_ponderaciones = pd.merge(
#       ids_variables_df,
#      ponderaciones,
#      on=)

#fandg_index = fear_and_greed_index(all_variables, vars_ponderaciones)





#Las variables se van a ir multiplicando por lo que el f & g index se
# actualizaria dia a dia peeero, podemos calcular uno frente al mes pasado
# según determinadas varibles p.e.










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



# inflaciones_mensuales = specific_request(27, january, today_date)
# reservas_int_mensuales = specific_request(1, january, today_date)
