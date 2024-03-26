import streamlit as st
import pandas as pd
import numpy as np
import functions

st.set_page_config(
    page_title='360 Blue Orders Report',
    page_icon='🧾'
)

st.caption('VACAYZEN')
st.title('Orders Report')
st.info('Classification of **360 Blue** orders, highlighting **Alaya** properties.')

with st.sidebar:
    ral_file = st.file_uploader('360 Blue Partner Site RAL', 'csv')
    ap_file  = st.file_uploader('Alaya_List',          'csv')
    da_file = st.file_uploader('360 Blue Partner Site Dispatch Activities', 'csv')


if ral_file is not None and ap_file is not None and da_file is not None:
    ral = pd.read_csv(ral_file)
    ap  = pd.read_csv(ap_file)
    da  = pd.read_csv(da_file)

    da.Dispatch           = pd.to_datetime(da.Dispatch).dt.date
    da['Completion Time'] = pd.to_datetime(da['Completion Time'])
    da                    = da.sort_values(by='Completion Time', ascending=False)
    da                    = da.drop_duplicates(subset=da.columns[:-1], keep='last')
    da                    = da.sort_values(by='Dispatch', ascending=False)

    st.download_button('DOWNLOAD DISPATCH ACTIVITY REPORT', data=da.to_csv(index=False), file_name='activity.csv', mime='csv', use_container_width=True, type='primary')

    ral['Address'] = ral.apply(functions.CombineAddress1and2, axis=1)
    ral            = ral.dropna(subset='Address')
    ral.Start      = pd.to_datetime(ral.Start).dt.date
    ral.End        = pd.to_datetime(ral.End).dt.date

    l, r      = st.columns(2)
    units     = l.selectbox('Unit Code Column', options=ap.columns)
    addresses = r.selectbox('Address Column',   options=ap.columns)
    startDate = l.date_input('Start of Range')
    endDate   = r.date_input('End of Range', value=startDate+pd.Timedelta(days=14), min_value=startDate)

    ap['Address'] = ap[addresses]

    if st.button('Begin', use_container_width=True):

        def GetValidOrders(row):
            if pd.isna(row.Start):
                return False
            
            return ((row.Start >= startDate) & (row.Start <= endDate))
    
        ral['Valid'] = ral.apply(GetValidOrders, axis=1)
        valid        = ral[ral.Valid].RentalAgreementID.unique()
        ral          = ral[ral.RentalAgreementID.isin(valid)]
        
        with st.status('Getting address data...', expanded=True) as status:
            
            st.write('Getting **Alaya** addresses...')
            ap['google_address']  = ap.apply(functions.ApplyGoogleAddress,axis=1)
            
            st.write('Getting **orders** addresses...')
            ral['google_address'] = ral.apply(functions.ApplyGoogleAddress,axis=1)
            ral['google_address'] = ral.apply(functions.RemoveFloridaUSA,axis=1)

            status.update(label='Address data acquired!', expanded=False, state='complete')


        result = pd.merge(left=ral, right=ap, left_on='google_address', right_on='google_address', how='left')
        result = result.drop(['Valid','Address 1','Address 2','Address_y','google_address',addresses], axis=1)
        result = result.rename(columns={'Address_x': 'Address', units: 'Type'})
        result.Type = result.apply(functions.ChangeUnitToAlaya, axis=1)
        result.insert(0,'Type',result.pop('Type'))
        result.insert(3,'Address',result.pop('Address'))
        result = result.sort_values(by='RentalAgreementID')

        st.download_button(label='DOWNLOAD ORDERS REPORT', data=result.to_csv(index=False), file_name=f'orders_{str(startDate)}_{str(endDate)}.csv', mime='csv', use_container_width=True, type='primary')