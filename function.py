
import quandl
import pickle
import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go


#Download and cache Quandl Dataseries
#=====================================

def get_quandl_data(quandl_id):
    
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

#Allow to merge a single column of each dataframe into a new combined dataframe
#==============================================================================
    
def merge_dfs_on_column(dataframes, labels, col): 
    
    series_dict = {}
    for index in range(len(dataframes)): 
        series_dict[labels[index]] = dataframes[index][col]
    return pd.DataFrame(series_dict)


#Function allowing to download and cache JSON data, return as a dataframe
#=========================================================================
    
def get_json_data(json_url, cache_path):
    try:        
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(json_url))
    except (OSError, IOError) as e:
        print('Downloading {}'.format(json_url))
        df = pd.read_json(json_url)
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(json_url, cache_path))
    return df

#Plot a correlation heatmap for the entire dataframe
#===================================================

def correlation_heatmap(df, title, absolute_bounds=True):
    
    heatmap = go.Heatmap( 
            
            z = df.corr(method= 'spearman').as_matrix(),
            x = df.columns,
            y = df.columns, 
            colorbar = dict(title='Spearman Coefficient'),
            )
    layout = go.Layout(title=title)
    if absolute_bounds: 
        heatmap['zmax'] = 1.0
        heatmap['zmin'] = -1.0
    fig = go.Figure(data=[heatmap], layout = layout)
    py.iplot(fig)


