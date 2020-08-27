import streamlit as st
import pandas as pd
import numpy as np
import investpy
import time
import base64

from io import BytesIO
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import date, timedelta

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    val = to_excel(df)
    b64 = base64.b64encode(val)  
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="dati_settimanale.xlsx">Download csv file</a>' 


st.title('Come sono andati i mercati questa settimana?')
st.write('Overview super generica sui mercati e link per il download del csv in fondo alla pagina.')

def fun():
    st.write('Ecco i dati! :)')
    ## Dati dello Spread da Borsa Italiana
    url = 'https://borsaitaliana.teleborsa.it/pages/spread/item.aspx'
    try:
        page = urlopen(url)
    except:
        print("Error opening the URL")
    soup = BeautifulSoup(page, 'html.parser')
    content = soup.find('span',{'class':'t-text -size-lg -black-warm-60 text-bold'})
    spread = content.contents
    s = pd.DataFrame(spread)
    s = s.rename(columns={0:'perf_sett_%'})
    s['tipo'] = 'spread_btp_bund'
    s = s[['tipo','perf_sett_%']]

    ## Dati valutarii

    eur_usd = investpy.get_currency_cross_recent_data(currency_cross='EUR/USD')
    eur_gbp = investpy.get_currency_cross_recent_data(currency_cross='EUR/GBP')
    eur_yen = investpy.get_currency_cross_recent_data(currency_cross='EUR/JPY')

    # today = date.today()
    # today = today.strftime("%d/%m/%Y")
    # last_day = date.today() - timedelta(days=20)
    # last_day = last_day.strftime("%d/%m/%Y")

    ## Indici di mercato 

    df_it = investpy.get_index_recent_data(index='MSCI Italy Net EUR',country='italy') # italia
    # df_eu = investpy.get_index_recent_data(index='MSCI Europe Net EUR',country='euro zone') # europa
    df_us = investpy.get_index_recent_data(index='MSCI US Net USD',country='united states') # usa
    df_jp = investpy.get_index_recent_data(index='MSCI Japan Net JPY',country='japan') # japan
    df_ci = investpy.get_index_recent_data(index='MSCI China Net USD',country='china') # china
    # df_mt = investpy.get_index_recent_data(index='MSCI World Info Tech Net USD',country='world') # mondo tech
    # df_em = investpy.get_index_recent_data(index='MSCI EM Net USD',country='world') # emergenti
    # df_ge = investpy.get_index_recent_data(index='TR Eurozone 10 Years Government Benchmark',country='euro zone') # governativo eurozona
    df_gu = investpy.get_index_recent_data(index='TR US 10 Year Government Benchmark',country='united states') # governativo usa
    df_iu = investpy.get_index_recent_data(index='DJ Equal Weight US Issued Corporate Bond TR',country='united states') # ig corp usa 
    # df_or = investpy.get_index_recent_data(index='Bloomberg Gold TR',country='world') # oro 
    df_wt = investpy.get_index_recent_data(index='Bloomberg WTI Crude Oil TR',country='world') # wti
    # df_wt = investpy.get_index_historical_data(index='Bloomberg WTI Crude Oil TR',country='world',from_date=last_day,to_date=today,interval='Daily') # wti

    ## Creo dataframe finale

    # index = [df_it,df_eu,df_us,df_jp,df_ci,df_mt,df_em,df_ge,df_gu,df_iu,df_or,df_wt,eur_gbp,eur_usd,eur_yen]
    index = [df_it,df_us,df_jp,df_ci,df_gu,df_iu,df_wt,eur_gbp,eur_usd,eur_yen]

    val_all = []
    for i in range(len(index)):
        val = ((index[i][['Close']].iloc[-1].values / index[i][['Close']].iloc[-5].values)-1)*100
        val_all.append(val)
    val_all = pd.DataFrame(val_all)
    val_all = val_all.rename(columns={0:'perf_sett_%'})
    val_all['tipo'] = 'nome_indice_da_inserire'

    # val_all['tipo'][0] = 'azioni_italia'
    # val_all['tipo'][1] = 'azioni_europa'
    # val_all['tipo'][2] = 'azioni_usa_usd'
    # val_all['tipo'][3] = 'azioni_japan_yen'
    # val_all['tipo'][4] = 'azioni_cina_usd'
    # val_all['tipo'][5] = 'azioni_world_info_tech_usd'
    # val_all['tipo'][6] = 'azioni_emergenti_usd'
    # val_all['tipo'][7] = 'bond_governativi_eurozona'
    # val_all['tipo'][8] = 'bond_governativi_usa'
    # val_all['tipo'][9] = 'bond_corporate_usa'
    # val_all['tipo'][10] = 'oro'
    # val_all['tipo'][11] = 'wti'
    # val_all['tipo'][12] = 'euro_sterlina'
    # val_all['tipo'][13] = 'euro_dollaro'
    # val_all['tipo'][14] = 'euro_yen'

    val_all['tipo'][0] = 'azioni_italia'
    val_all['tipo'][1] = 'azioni_usa_usd'
    val_all['tipo'][2] = 'azioni_japan_yen'
    val_all['tipo'][3] = 'azioni_cina_usd'
    val_all['tipo'][4] = 'bond_governativi_usa'
    val_all['tipo'][5] = 'bond_corporate_usa'
    val_all['tipo'][6] = 'wti'
    val_all['tipo'][7] = 'euro_sterlina'
    val_all['tipo'][8] = 'euro_dollaro'
    val_all['tipo'][9] = 'euro_yen'

    # val_all['tipo'][0] = 'euro_sterlina'
    # val_all['tipo'][1] = 'euro_dollaro'
    # val_all['tipo'][2] = 'euro_yen'

    val_all = val_all[['tipo','perf_sett_%']]

    ## Aggancio i dati dello spread
    val_all = val_all.append(s)

    ## Genero un grafico semplice
    chart = st.table(val_all)
    time.sleep(1)
    ## Esporto nell'excel 

    # val_all.to_excel('dati_settimanali.xlsx')
    df = val_all
    st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    return

if st.button('Clicca qua per avviare aggiornamento dei dati'):
    fun()
