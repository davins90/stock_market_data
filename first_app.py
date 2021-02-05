import streamlit as st
import pandas as pd
import numpy as np
import investpy
import time
import base64

from io import BytesIO
from urllib.request import urlopen
from bs4 import BeautifulSoup

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    val = to_excel(df)
    b64 = base64.b64encode(val)  
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="dati_mercato.xlsx">Download csv file</a>' 


st.title("Come sono andati i mercati questa settimana e nell' ultimo mese?")
st.write('Una volta lanciato questo programma viene in automatico generato un excel con i dati aggiornati dei mercati.')

## Dati valutarii

eur_usd = investpy.get_currency_cross_recent_data(currency_cross='EUR/USD')
eur_gbp = investpy.get_currency_cross_recent_data(currency_cross='EUR/GBP')
eur_yen = investpy.get_currency_cross_recent_data(currency_cross='EUR/JPY')

## Dati dello Spread da Borsa Italiana

url = 'https://borsaitaliana.teleborsa.it/pages/spread/item.aspx'
def spread(url):
    try:
        page = urlopen(url)
    except:
        print("Error opening the URL")
    soup = BeautifulSoup(page, 'html.parser')
    content = soup.find('span',{'class':'t-text -size-lg -black-warm-60 text-bold'})
    spread = content.contents
    s = pd.DataFrame(spread)
    s = s.rename(columns={0:'perf_sett'})
    s['tipo'] = 'spread_btp_bund'
    s['perf_mese'] = 'non_disponibile'
    s = s[['tipo','perf_sett','perf_mese']]
    return s

s = spread(url)


## Indici di mercato 

df_it = investpy.get_index_recent_data(index='MSCI Italy Net EUR',country='italy') # italia
df_eu = investpy.get_index_recent_data(index='MSCI Europe Net EUR',country='euro zone') # europa
df_us = investpy.get_index_recent_data(index='MSCI US Net USD',country='united states') # usa
df_jp = investpy.get_index_recent_data(index='MSCI Japan Net JPY',country='japan') # japan
df_ci = investpy.get_index_recent_data(index='MSCI China Net USD',country='china') # china
df_mt = investpy.get_index_recent_data(index='MSCI World Info Tech Net USD',country='world') # mondo tech
df_em = investpy.get_index_recent_data(index='MSCI EM Net USD',country='world') # emergenti
df_ge = investpy.get_index_recent_data(index='TR Eurozone 10 Years Government Benchmark',country='euro zone') # governativo eurozona
df_gu = investpy.get_index_recent_data(index='TR US 10 Year Government Benchmark',country='united states') # governativo usa
df_iu = investpy.get_index_recent_data(index='DJ Equal Weight US Issued Corporate Bond TR',country='united states') # ig corp usa 
df_or = investpy.get_index_recent_data(index='Bloomberg Gold TR',country='world') # oro 
df_wt = investpy.get_index_recent_data(index='Bloomberg WTI Crude Oil TR',country='world') # wti

## Creo dataframe finale

index = [df_it,df_eu,df_us,df_jp,df_ci,df_mt,df_em,df_ge,df_gu,df_iu,df_or,df_wt,eur_gbp,eur_usd,eur_yen]
nomi = ['azioni_italia','azioni_europa','azioni_usa_usd','azioni_japan_yen','azioni_cina_usd','azioni_world_info_tech_usd','azioni_emer_usd','bond_gov_euro','bond_gov_usa','bond_corp_usa',
       'oro','wti','euro_sterlina','euro_dollaro','euro_yen']
val_all = pd.DataFrame(columns=['tipo','perf_sett','perf_mese'])

for (i,j),n in zip(enumerate(index),nomi):
    for z,t in enumerate(val_all):
        if z == 0:
            val_all.loc[i] = n
        elif z == 1:
            val_all.loc[i][z] = (((index[i][['Close']].iloc[-1].values / index[i][['Close']].iloc[-5].values)-1)*100).item()
        else:
            val_all.loc[i][z] = (((index[i][['Close']].iloc[-1].values / index[i][['Close']].head(1).values)-1)*100).item()

## Aggancio i dati dello spread
val_all = val_all.append(s)

## Genero un grafico semplice
chart = st.table(val_all)
time.sleep(1)

## Esporto nell'excel 

# val_all.to_excel('dati_settimanali.xlsx')
df = val_all
st.markdown(get_table_download_link(df), unsafe_allow_html=True)
