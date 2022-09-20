import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def process_data(df):
    f = df.T
    f.columns = f.loc['Unnamed: 0']
    f.drop('Unnamed: 0', inplace = True)
    f.reset_index(drop = True, inplace = True)
    
    return f


def sort_data(dataframe, by = 'RRT'):
    sort_df = dataframe.sort_values(by = by)
    return sort_df


def drop_same_rows(dataframe):
    sort_df = sort_data(dataframe)
    rrt_one = sort_df['RRT'] == 1
    x = sort_df[rrt_one]
    ids = x.index.values.tolist ()
    x = x.iloc[:, -3:]
    max_idx = x.mean(axis = 1).idxmax()
    ids_to_drop = [i for i in ids if i != max_idx]
    final_df = sort_df.drop(index = ids_to_drop)
    
    return final_df


def rearrange_data(df):
    f = process_data(df)
    final_df = drop_same_rows(f)
    final_df = final_df.T
    final_df.reset_index(inplace = True)
    final_df.columns = range(final_df.columns.size)
    return final_df


def fill_max(df):
    
    for i in range(1, df.shape[1]):
        for j in range(2, df.shape[0]):
            max_val = df.loc[2:, i].max()
            if df.loc[j, i] == max_val:
                pass
            else:
                df.loc[j, i] = max_val
                
    
    df = df.T
    df.columns = df.loc[0]
    df.drop(0, axis = 0, inplace = True)
    
    
    return df


def add_extra_rows(g):
    s_row = pd.Series([0] * len(g.columns), index = g.columns)
    g = g.reset_index(drop = True)
    
    for i in range(g.shape[0]):
        if i == 0:
            g.loc[-1] = s_row
        idx = i + 0.5
        g.loc[idx] = s_row
    
    g = g.sort_index().reset_index(drop=True)
    
    return g


def fill_rt_rrt(extra_row_df):
    i = 0
    while(i < extra_row_df.shape[0] - 1):
        mean_rt = 0
        mean_rrt = 0
        if i == 0:
            mean_rt = (extra_row_df.loc[i, 'RT']  + extra_row_df.loc[i + 1, 'RT']) / 2
            mean_rrt = (extra_row_df.loc[i, 'RRT'] + extra_row_df.loc[i + 1, 'RRT']) / 2

            extra_row_df.loc[i, 'RT'] = mean_rt
            extra_row_df.loc[i, 'RRT'] = mean_rrt


        elif i + 2 == extra_row_df.shape[0]:
            extra_row_df.loc[i + 1, 'RT'] = extra_row_df.loc[i, 'RT'] + 0.05
            extra_row_df.loc[i + 1, 'RRT'] = extra_row_df.loc[i , 'RRT'] + 0.05


        else:
            mean_rt = (extra_row_df.loc[i, 'RT']  + extra_row_df.loc[i + 2, 'RT']) / 2
            mean_rrt = (extra_row_df.loc[i, 'RRT'] + extra_row_df.loc[i + 2, 'RRT']) / 2

            extra_row_df.loc[i + 1, 'RT'] = mean_rt
            extra_row_df.loc[i + 1, 'RRT'] = mean_rrt
        
            i += 1
        i += 1
    
    return extra_row_df





def chromotogram_data(rearrange_df):
    # f = process_data(df)
    # final_df = drop_same_rows(f)
    # sp3_table_df = rearrange_data(final_df)

    g = fill_max(rearrange_df)
    extra_row_df = add_extra_rows(g)
    chromotogram_df = fill_rt_rrt(extra_row_df)

    return chromotogram_df





#########################
### Bubble Plot #########
######################## 

def bubble_data(df):
    f = process_data(df)
    final_df = drop_same_rows(f)
    new_df = rearrange_data(final_df)
    new_df = new_df.T
    new_df.columns = new_df.iloc[0, :]
    new_df.drop(0, axis = 0, inplace = True)

    return new_df


def fill_missing_val(df):
    n_d = bubble_data(df)
    n_d = n_d.fillna(0)
    
    return n_d 

def add_cols(df):
    n_d = fill_missing_val(df)
    
    for i in range(n_d.shape[1] - 2):
        n_d.insert(loc = len(n_d.columns),
                  column = str(i + 1) + 'const',
                  value = [i + 1 for j in range(n_d.shape[0])])
    
    return n_d


def bubble_plot(df):
    bubble_df = add_cols(df)

    return bubble_df


def calculate_extra_col(d):
    const_col = 0
    for i in range(d.shape[1]):
        if str(i) + 'const' in list(d.columns):
            const_col += 1
    
    return const_col


def bubble_figure_data(d):
    const_col = calculate_extra_col(d)
    
    figures = []
    colors = ['red', 'blue', 'green', 'purple', 'grey', 'cyan', 'brown']

    for i in range(const_col):
        x = px.scatter(d, x="RRT", y= d.iloc[:, 2 + const_col + i], size = d.iloc[:, i + 2].to_list(), log_x=True, size_max=50)
        x.update_traces(marker=dict(color= colors[i]))

        figures.append(x)
    
    x = tuple()
    for i in range(len(figures)):
        x += figures[i].data
    
    return x