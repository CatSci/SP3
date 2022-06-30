import pandas as pd
import streamlit as st
import numpy as np
from collections import OrderedDict
import math
import openpyxl


st.write('# SP3 Table')

def read_rt(file, sheet_name):
    """Return a list

    extract all retention time from different time reaction
    """
    rt_list = []
    for i in sheet_name:
        df = pd.read_excel(file , sheet_name = i)
        rt_col = df['RT']
        rt_list.append(rt_col)
    
    rt = [i for sub_list in rt_list for i in sub_list]
    return rt

def add_data(file, sheets, dataframe):
    """Return a dataframe

    add data from different screen reaction time
    """
    for i in sheets:
        d = pd.read_excel(file, sheet_name = i)

        dataframe[i] = pd.DataFrame([[np.nan]], index = dataframe.index)
        for idx, val in d.iterrows():
            area, rt_val = val['Total Area %'], val['RT']
            dataframe.at[dataframe.index[dataframe.RT == rt_val].tolist(), i] = area
    
    transpose_sp3 = dataframe.T
    transpose_sp3.reset_index(inplace=True)
    transpose_sp3 = transpose_sp3.rename(columns = {'index':'Unnamed: 0'})
    return transpose_sp3

def find_same_col(df_file):
    """Return a dictionary

    to find if the two nearby values of retention time is almost same or not
    if its the same we need to drop it
    """
    SP3 = df_file
    yes = {}
    for i in range(SP3.shape[1] - 2):
        x = SP3.iloc[0, i + 1]
        y = SP3.iloc[0, i + 2]
        if y - x <= 0.05:
            yes[i + 2] = y
        else:
            pass

    return yes

def drop_col(df, rt_val = 16.69, col = 113): 
    """Return a dataframe and the values of the column we need to drop

    to extract similar column values and drop the column
    """
    a = {}
    for i in range(df.shape[0] - 1):
        p = df.iloc[i + 1, col]
        t = i + 1
        a[t] = p
    
    # drop that column
    df.drop([col - 1], axis = 1, inplace = True)
    return df , a


def replace_val(df, drop_col_val, col = 112):
    """Return a dataframe

    to replace the value in nearby column 
    """
    for i in range(df.shape[0] - 1):
        if math.isnan(drop_col_val[i + 1]):
            pass
        else:
            df.iloc[i + 1, col] = drop_col_val[i + 1]
    return df

def sp3_table(df, rev):
    """Returns a dataframe

    columns will be drop and then values will be replaced
    """
    for key, value in rev.items():
        new_df, a = drop_col(df = df, rt_val = value, col = key)
        final_df = replace_val(df = new_df, drop_col_val = a, col = key - 1)
    
    return final_df


def add_rrt(dataframe):
    """Return a dataframe

    add rrt column in dataframe
    """
    max_area = dataframe['Total Area %'].max()
    rt_max = dataframe['Total Area %'].idxmax()
    dataframe['RRT'] = dataframe['RT'] / dataframe['RT'].iloc[rt_max]
    
    return dataframe
    
    
def fill_rrt(file, sheets, df):
    """Returns a dataframe

    fill the rrt value in dataframe
    """
    for i in sheets:
        d = pd.read_excel(file, sheet_name = i)
        row = d.shape[0]
        d = add_rrt(d)        # dataframe with rrt column
        for x in range(d.shape[0]):
            rrt_val = d.loc[x, 'RRT']  # rrt_value
            rt_val = d.loc[x, 'RT']
            idx = df.index[(df["RT"]== rt_val)]     # find index position for rt value in sp3
            df.iloc[idx, 1] = rrt_val

    return df

uploaded_file = st.file_uploader("Choose a file")

def create_sp3_table():   
     if uploaded_file is not None:
          wb = openpyxl.load_workbook(uploaded_file)
          sheets = wb.sheetnames

          rt_list = read_rt(uploaded_file, sheets)
          rt_list.sort()
          SP3 = pd.DataFrame({'RT' : rt_list, 'RRT': np.nan})
          
          SP3 = fill_rrt(uploaded_file, sheets, df = SP3)
          # call add_data
          SP3 = add_data(uploaded_file, sheets, dataframe = SP3)

          # call find same col
          same_col = find_same_col(SP3)
          rev = OrderedDict(reversed(list(same_col.items())))

          final_df = sp3_table(df = SP3, rev = rev)
          return final_df.to_csv().encode('utf-8')

# blue #0C1B2A
# orange #F6931D

# div.stButton > button:hover {
#     background-color: #F6931D;
#     color:#ffffff;
#     }

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0C1B2A;
    color:#ffffff;
    border:None;
}

</style>""", unsafe_allow_html=True)

if st.button('Create SP3 Table'):
     csv = create_sp3_table()
     st.download_button(
     label="Download SP3 Table as CSV",
     data=csv,
     file_name='sp3_table.csv',
     mime='text/csv',
     
 )






