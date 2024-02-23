import streamlit as st
import pandas as pd
import requests

def CombineAddress1and2(row):
    if pd.isna(row['Address 1']): return None
    if pd.isna(row['Address 2']): return str(row['Address 1']).upper()
    
    add1 = str(row['Address 1']).upper()
    add2 = str(row['Address 2']).upper()

    if 'UNIT' or '#' in add1: return str(row['Address 1']).upper()

    return (str(row['Address 1']) + ' ' + str(row['Address 2'])).upper()


def GetGoogleAddress(address):
    if pd.isna(address) or address == '' or address == None: return None

    print(address)
    address = address.replace(' ','+')
    address = address + '+FL+32459'

    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + st.secrets['GEO_API_KEY']
    response = requests.get(url)
    json     = response.json()
    
    try:
        return json['results'][0]['formatted_address']
    except:
        return None


def ApplyGoogleAddress(row):
    if pd.isna(row.Address):
        return None
    
    return GetGoogleAddress(row.Address)


def RemoveFloridaUSA(row):
    if row.google_address == 'Florida, USA':
        return None
    
    return row.google_address


def ChangeUnitToAlaya(row):
    if pd.isna(row.Type):
        return '360 Blue'
    
    return 'Alaya'