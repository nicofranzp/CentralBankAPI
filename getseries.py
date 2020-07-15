import zeep
import pandas as pd
from zeep.helpers import serialize_object
import datetime as dt
import numpy as np
from time import sleep
import sys

def getSeries(user,pw,fInic,fFin,series):
    
    # Inputs
    user=str(user)
    pw=str(pw)
    fInic=str(fInic)
    fFin=str(fFin)
    
    if type(series)==list:
        pass
    else:
        series=[str(series)]
        
    series=[x.upper() for x in series]
        
    # Validation of codes
    for ser_cod in reversed(series):
        if ser_cod[-1].lower() in ["d","m","t","a"]:
            pass
        else:
            print("Series " + ser_cod + " not found. Double check the code name")
            series.remove(ser_cod)
    
    # Frequencies of each series
    series_freq=[x[-1] for x in series]
    series_freq=list(np.unique(series_freq))
    
    # Frequency initial
    
    for x in range(len(series_freq)):
        if series_freq[x]=="D":
            series_freq[x]=series_freq[x].replace("D","DAILY")
        elif series_freq[x]=="M":
            series_freq[x]=series_freq[x].replace("M","MONTHLY")
        elif series_freq[x]=="T":
            series_freq[x]=series_freq[x].replace("T","QUARTERLY")
        elif series_freq[x]=="A":
            series_freq[x]=series_freq[x].replace("A","ANNUAL")
        else:
            pass
    
    #WSDL (Web Service Definition Language)  address 
    wsdl="https://si3.bcentral.cl/SieteWS/SieteWS.asmx?wsdl"
    client = zeep.Client(wsdl)
    
    #meta_series will collect data
    meta_series=pd.DataFrame()

    #Se itera dentro de la lista series_freq para consultar las distintas frecuencias de interés:
    for frequ in series_freq:#frequ=series_freq[0]
        for attempt in range(4):
            try:
                #Se consulta usando el usuario, password y frecuencia de interés
                res_search=client.service.SearchSeries(user,pw,frequ)
                #Se limpia la información obtenida
                res_search=res_search["SeriesInfos"]["internetSeriesInfo"]
                res_search = serialize_object(res_search)
                #Se crea un diccionario con las series obtenidas y los datos de interés (título, código y frencuencia)
                res_search = {serie_dict['seriesId']:[serie_dict['englishTitle'],serie_dict['frequency'], serie_dict['observed']] for serie_dict in res_search}
                #A partir del diccionario creado, se arma un dataframe (meta_series_aux) que luego se agrega al dataframe
                #que contendrá todas las frecuencias (meta_series)
                meta_series_aux=pd.DataFrame.from_dict(res_search,orient='index')
                meta_series=meta_series.append(meta_series_aux)
                print("Frequency " + str(frequ) + " found. Adding")
                break
            except:
                print("Try number " + str(attempt) + ": the frequency " + str(frequ) + " was not found")
                #En caso de error, se esperan 20 segundos antes de volver a consultar la serie
                sleep(20)
        else:
            print("Frequency " + str(frequ) + " not found. aborting execution")
            sys.exit("ABORTING")

    #Finalmente, se limpia el Dataframe obtenido para conservar sólo las series de interés:
    meta_series=meta_series.loc[series]
    meta_series.columns=["englishTitle","frequency", "observed"]
    
    #Creación del DataFrame values_df, que incluirá todas las series que se consultarán.
    values_df=pd.DataFrame()
    #Iteración por cada una de las series consultando los datos. Los valores obtenidos se agregan a values_df
    for serieee in series:
        #Se genera un loop para hacer 10 intentos de consulta por serie. Si tiene éxito, continúa con la siguiente serie, si no tiene éxito, intenta nuevamente.
        for attempt in range(4):
            try:
                #Creación del objeto que contendrá el código de serie       
                ArrayOfString = client.get_type('ns0:ArrayOfString')
                value = ArrayOfString(serieee)
                
                #Se ejecuta la consulta utilizando los parámetros ingresados (usuario, password, fecha de inicio, fecha final y código de serie) y se asigna a la variable result
                result = client.service.GetSeries(user,pw,fInic,fFin, value)
                #Se omite la serie si no hay observaciones en el período solicitado
                if result["Series"]["fameSeries"][0]["obs"]==[]:
                    print("The variable "+ str(serieee) + " does not have data for the selected period")
                    break
                #Se limpia la información obtenida, dejando como nombre de fila el código de serie y, como columnas, las fechas en formato dd-mm-aaaa
                result = serialize_object(result["Series"]["fameSeries"][0]["obs"])
                result=pd.DataFrame(result).T
                result.columns=result.iloc[0,:]
                result=result.drop(result.index[0:3],axis=0)
                result.index=[serieee]
                
                #Se agrega la serie ordenada al DataFrame values_df
                
                values_df=values_df.append(result,sort=True)
                print("Series " + str(serieee) + " found. Adding")
                break
            except:
                print("Try number " + str(attempt) + ": the variable " + str(serieee) + " was not found")
                #En caso de error, se esperan 20 segundos antes de volver a consultar la serie
                sleep(20)
        else:
            print("Series " + str(serieee) + " not found. Omitting")
    
    #Se guarda en new_col los nombres de las columnas de values_df
    new_col=list(values_df.columns)
    #Se ordenan las fechas de new_col para asegurar su disposición desde la más antigua a la más nueva
    new_col.sort(key = lambda date: dt.datetime.strptime(date, '%d-%m-%Y'))
    #Se ordena el dataframe values_df con el orden descrito en la línea anterior
    values_df=values_df[new_col]
    #Se unen los resultados de meta_series con values_df en final_dic
    final_dic=pd.merge(meta_series,values_df,left_index=True,right_index=True)
    #Se separan las salidas para obtener un dataframe por frecuencia
    final_dic = dict(iter(final_dic.groupby('frequency')))
    final_dic.update((x, y.dropna(axis=1,how="all")) for x, y in final_dic.items())
    
    #Se devuelve el resultado de final_dic
    return final_dic