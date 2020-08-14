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
    
    # Iteration to find frequencies
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
                # If error, wait 20 secs
                sleep(20)
        else:
            print("Frequency " + str(frequ) + " not found. aborting execution")
            sys.exit("ABORTING")

    # cleaning data_frame to get only the desired serirs
    meta_series=meta_series.loc[series]
    meta_series.columns=["englishTitle","frequency", "observed"]
    
    # values_df, will contain series to be downloaded.
    values_df=pd.DataFrame()
    # iteration for each series
    for serieee in series:
        # the algorithm will try 4 times to download
        for attempt in range(4):
            try:
                ArrayOfString = client.get_type('ns0:ArrayOfString')
                value = ArrayOfString(serieee)
                
                # Download the series
                result = client.service.GetSeries(user,pw,fInic,fFin, value)
                # Omitting variables without data
                if result["Series"]["fameSeries"][0]["obs"]==[]:
                    print("The variable "+ str(serieee) + " does not have data for the selected period")
                    break
                # clean up
                result = serialize_object(result["Series"]["fameSeries"][0]["obs"])
                result = pd.DataFrame(result).T
                result.columns = result.iloc[0,:]
                result = result.drop(result.index[0:3],axis=0)
                result.index = [serieee]
                
                # adding the new serie (sorted) to values_df
                
                values_df=values_df.append(result,sort=True)
                print("Series " + str(serieee) + " found. Adding")
                break
            except:
                print("Try number " + str(attempt) + ": the variable " + str(serieee) + " was not found")
                # If error wait 20 seconds
                sleep(20)
        else:
            print("Series " + str(serieee) + " not found. Omitting")
    
    
    new_col=list(values_df.columns)
    new_col.sort(key = lambda date: dt.datetime.strptime(date, '%d-%m-%Y'))
    values_df=values_df[new_col]
    final_dic=pd.merge(meta_series,values_df,left_index=True,right_index=True)
    final_dic = dict(iter(final_dic.groupby('frequency')))
    final_dic.update((x, y.dropna(axis=1,how="all")) for x, y in final_dic.items())
    
    return final_dic