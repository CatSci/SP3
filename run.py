import pandas as pd
import streamlit as st
import numpy as np
from collections import OrderedDict
import math
import openpyxl
import plotly.express as px
import plotly.graph_objects as go

from utils import chromotogram_data, bubble_plot, bubble_figure_data

st.markdown('**Note - Please do not post target or intermediate structure information externally**.')
st.title('SP3 Table')

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
        # st.write(i)
        # st.write(dataframe)
        for idx, val in d.iterrows():
            area, rt_val = val['Total Area %'], val['RT']
            # st.write(area)
            # st.write(rt_val)
            # index = dataframe.index[dataframe.RT == rt_val].tolist()
            # st.write(index[0])
            # dataframe.loc[index, i] = area
            # st.write(dataframe)
            # st.write(dataframe.index[dataframe.RT == rt_val].tolist(), str(i))
            dataframe.at[dataframe.index[dataframe.RT == rt_val].tolist()[0], str(i)] = area
            # st.write(dataframe)
    
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

# def create_sp3_table(): 
    
#     if uploaded_file is not None:
#       wb = openpyxl.load_workbook(uploaded_file)
#       sheets = wb.sheetnames
        
#       rt_list = read_rt(uploaded_file, sheets)
#       rt_list.sort()
#       SP3 = pd.DataFrame({'RT' : rt_list, 'RRT': np.nan})

#       SP3 = fill_rrt(uploaded_file, sheets, df = SP3)
#       # call add_data
#       SP3 = add_data(uploaded_file, sheets, dataframe = SP3)

#       # call find same col
#       same_col = find_same_col(SP3)
#       rev = OrderedDict(reversed(list(same_col.items())))

#       final_df = sp3_table(df = SP3, rev = rev)
#       return final_df.to_csv().encode('utf-8')
    

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
          sp3_table_df, chromotogram_df = chromotogram_data(final_df)
          bubble_df = bubble_plot(final_df)

     return sp3_table_df.to_csv().encode('utf-8'), chromotogram_df, bubble_df, final_df.to_csv().encode('utf-8')


# hide streamlit style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)
# background-color: #ed9439;
st.markdown("""
<style>
.navbar {
  height: 80px;
  background-color: #ed9439;
  color: #ed9439;
}
.navbar-brand{
    font-size: 40px;
    margin-left:40px;
}
</style>""", unsafe_allow_html= True)


st.markdown("""
<nav class="navbar fixed-top navbar-expand-lg navbar-dark">
  <a class="navbar-brand" href="#" target="_blank">CatSci</a>
  

</nav>
""", unsafe_allow_html=True)



st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #ed9439;
    color:#0f1b2a;
    border:None;
}
div.stButton > button:first-child:focus {
    background-color: #ed9439;
    color:#0f1b2a;
    border:None;
}
</style>""", unsafe_allow_html=True)

if st.button('Create SP3 Table'):
    sp3, chromotogram_df, bubble_df, final_df = create_sp3_table()
    st.download_button(
     label="Download SP3 Table as CSV",
     data=final_df,
     file_name='sp3_table.csv',
     mime='text/csv',)

    # chromotogram plot
    st.header('Chromatogram Plot')
    chromo_fig = px.line(chromotogram_df, x="RRT", y= chromotogram_df.iloc[:, -1], markers = True, range_y = [0, 100])
    st.plotly_chart(chromo_fig)

    # bubble plot
    figure_data = bubble_figure_data(bubble_df)
    bubble_fig = go.Figure(data = figure_data)
    bubble_fig.update_layout(xaxis_title="RRT", yaxis_title="Sample number")

    st.header('Interactive Peak Map')
    st.plotly_chart(bubble_fig, x = 'RRT')






